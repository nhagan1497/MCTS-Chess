from UCTModel import UCTModel
from ChessModel import ChessModel
from UCTChessDB import UCTChessDB

class UCTModelChess(UCTModel):
    def __init__(self, db_name='chessv1.db', db_table='ChessTable'):
        self.model = ChessModel()

        self.db = None
        self.db_name = db_name
        self.db_table = db_table
        self.db = UCTChessDB(db_name=db_name, db_table=db_table)
        #self.max_value = -1

    def set_state(self, state):
        # Sets current fen of the chess model
        self.model.set_fen(state)

    def get_state(self):
        # Returns FEN of current state
        return self.model.fen()

    def get_actions(self):
        # Returns list of states that can be transitioned into
        return self.model.get_move_list_fen()

    def get_terminal_reward(self):
        # Returns reward obtained from being in a terminal state
        # This reward will be for the person whose turn it is
        return self.model.basic_rating()

    def is_terminal_state(self):
        # Returns whether current state is terminal or not
        return self.model.is_game_over()

    def get_value(self):
        # Returns heuristic value for current state
        # This will be the reward for the person who just moved, not the person whose turn it is
        # Ideally this will be a neural network returning values between 0 and 1

        #If a stored value exists, use it first
        db_value = self.db.get_value(self.get_state())
        if db_value is not None:
            return db_value

        if self.model.is_checkmate():
            # If it's checkmate, return arbitrarily large reward for winning the game. Value is 3x the highest recorded number from this value function
            return 600

        self.model.turn = not self.model.turn
        value = self.model.basic_rating()
        self.model.turn = not self.model.turn

        #if value > self.max_value:
        #   self.max_value = value
        #   print(f'\nNew Max Value: {self.max_value}\n')
        return value

    def save_state(self, fen, visits, total_reward):
        self.db.set_value(fen, visits, total_reward)

    def new_model(self):
        return_value = UCTModelChess()
        return_value.set_state(self.get_state())
        return return_value

    def open_db(self, read_only=True):
        self.db.open_db(read_only=read_only)


    def close_db(self):
        self.db.close_db()