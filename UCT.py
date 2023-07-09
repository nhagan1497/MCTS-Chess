import math
import random
from multiprocessing import Pool
from copy import copy

from UCTModel import UCTModel
from UCTModelChess import UCTModelChess

# TO DO:
#   Grab all child states at once to optimize time spent reading from db


######################### Notes #########################
# Each Child holds the expected value for the player who moves into its state
# This value is not for the player whose turn it is in that state
# To inform decision making, a player must look into its child states whose values give the reward for moving into them
#
# The get_value function gives the value for the player who just moved into that state, not the player whose turn it is
# The get_terminal_reward function provides the value for the player whose turn it currently is, but is less informed than iterating over children
#
# This is messier than it needs to be since the heuristic isn't measuring something zero sum - like win probability or pawns of advantage
# If win probability was being measured, for example, all the stored values could be for one player and
#    the other player would subtract from one, or take the min instead of the max and values could propagate through every layer
# I'll have to change this when implementing a Neural Network which will attempt to predict win probabilities for either player directly

class Node:
    def __init__(self, state=None, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.total_reward = 0
        self.terminal_reward = 0

    def __str__(self):
        return_string = ''
        return_string += f'State: {self.state}\n'
        return_string += f'Visits: {self.visits}\n'
        return_string += f'Avg Reward: {self.total_reward / self.visits}\n'
        return return_string

    def get_ucb(self, constant):
        return (self.total_reward / self.visits) + math.sqrt(math.log(self.parent.visits) / self.visits) * constant

    def add_reward(self, reward):
        self.total_reward += reward
        self.visits += 1

    def get_reward(self):
        if not self.children:
            return self.terminal_reward
        best_child = max(self.children, key=lambda child: (child.total_reward / child.visits))
        return best_child.total_reward / best_child.visits

class UCT:
    def __init__(self, constant, iterations, model : UCTModel):
        # constant is used in determining exploration vs exploitation in UCB formula
        # iterations determines the number of loops before returning an action
        # model is of type UCTModel and provides information about state transitions and rewards
        # turn keeps track of whether children rewards should be positive or negative
        self.constant = constant
        self.iterations = iterations
        self.model = model

        # Creates root node
        self.root = Node(state=model.get_state())

    def get_best_child(self, node):
        return max(node.children, key=lambda child: child.get_ucb(self.constant))

    def pick_rand_child(self, children):
        # Pick random child weighted by their values, used for training so the same game isn't played repeatedly
        weights = []
        for child in children:
            weights.append(child.get_ucb(self.constant))
        return random.choices(children, weights)[0]

    def run_simulation(args):
        (self, root_state, model, iterations) = args
        def initialize_node(parent, model):
            #Adds children to node
            model.set_state(parent.state)
            child_states = model.get_actions()

            if not child_states:
                # Parent must be a terminal state
                reward = model.get_value()
                parent.add_reward(reward)
                parent.terminal_reward = model.get_terminal_reward()

            for state in child_states:
                # Creates node for each potential state transition
                child = Node(state=state, parent=parent)

                model.set_state(child.state)
                child.add_reward(model.get_value())

                parent.children.append(child)

        # Sets model state and checks for terminal state
        model.set_state(root_state)
        if len(model.get_actions()) == 0:
            print("In terminal state.")
            return None

        model.open_db()

        root = Node(state=root_state)
        root.add_reward(model.get_value())
        initialize_node(root, model)

        current_node = root

        for x in range(iterations):
            #Traverses down the tree until a leaf node is found
            while current_node.children != []:
                best_child = self.get_best_child(current_node)
                current_node = best_child

            #Once a leaf node is reached, it must be initialized and its value is propagated up the tree
            initialize_node(current_node, model)

            #This value function is only meaningful to one side or the other so the value is propagated only to the same player
            new_reward = current_node.get_reward()

            #The get reward function picks the best child's reward and returns it
            #Since the reward came from the children, it will go into the parent so that every other layer has it
            #  and same_player needs to start as True
            same_player = True

            #The loop stops on the root node
            while current_node.parent != None:
                current_node = current_node.parent
                if same_player:
                    current_node.add_reward(new_reward)

                # Skips every other layer
                same_player = not same_player

        model.close_db()
        return root

    def get_action(self, threads=1):
        if threads == 1:
            self.root = UCT.run_simulation((self, self.root.state, self.model, self.iterations))
        else:
            with Pool(processes=threads) as pool:
                fen_list = self.model.get_actions()
                iterations = int(self.iterations / len(fen_list)) + 1
                args = []
                for fen in fen_list:
                    new_model = self.model.new_model()
                    args.append((self, fen, new_model, iterations))

                self.root.children = pool.map(UCT.run_simulation, args)

        best_child = max(self.root.children, key=lambda child: (child.total_reward / child.visits))
        return best_child.state

    def take_action(self, new_state):
        def _save_child_states(node):
            for child in node.children:
                _save_child_states(child)
            self.model.save_state(node.state, node.visits, node.total_reward)

        self.model.open_db(read_only=False)
        _save_child_states(self.root)
        self.model.close_db()

        self.model.set_state(new_state)
        self.root = Node(state=new_state)