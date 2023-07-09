from time import time

from UCTModelChess import UCTModelChess
from ChessModel import ChessModel
from UCT import UCT

def model_test():
    model = UCTModelChess('rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1')

def uct_test(time_to_stop):
    model = UCTModelChess()
    uct = UCT(constant=1.2, iterations=1000, model=model)
    new_state = ''

    for x in range(20):
        new_state = uct.get_action(threads=24)
        if new_state is None:
            break
        uct.take_action(new_state)
        print(model.model)
        print('\n')
        if time() > time_to_stop:
           return
    print(new_state)

if __name__ == '__main__':
    seconds = time()
    # 10 minutes of run time
    time_to_stop = seconds + 600
    for x in range(20):
        uct_test(time_to_stop)
        if time() > time_to_stop:
            break