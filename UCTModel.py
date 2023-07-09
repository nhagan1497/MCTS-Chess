class UCTModel():
    def set_state(self, state):
        # Sets current state of model
        raise NotImplementedError

    def get_state(self, state):
        # Returns compact form of current state
        raise NotImplementedError

    def get_actions(self):
        # Returns list of states that can be transitioned into
        raise NotImplementedError

    def get_terminal_reward(self):
        # Returns reward obtained from being in a terminal state
        # This reward will be for the person whose turn it is
        raise NotImplementedError

    def is_terminal_state(self):
        # Returns whether current state is terminal or not
        raise NotImplementedError

    def get_value(self):
        # Returns heuristic value for current state
        # This will be the reward for the person who just moved, not the person whose turn it is
        raise NotImplementedError

    def save_state(self, state, visits, total_value):
        # Stores the given node values for later retrieval
        # Ensures progress is not lost when changing the root node
        raise NotImplementedError

    def new_model(self):
        # Returns copy of a new model
        # Lets UCT make copies for multiprocessing without knowing what the underlying model is
        raise NotImplementedError

    def open_db(self, read_only=True):
        # Open a connection to the database
        # Doesn't happen automatically for multiprocessing
        raise NotImplementedError

    def close_db(self):
        # Closes connection to the database
        raise NotImplementedError
