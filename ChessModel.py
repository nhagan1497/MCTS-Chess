import chess

STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1'

class ChessModel(chess.Board):
    #Extends python-chess board object with a few extra functions
    def __init__(self, starting_state=chess.STARTING_FEN):
        super().__init__(fen=starting_state)

    def get_binary(self):
        #### Converts FEN into a bitboard, the final bitboard contains (in order): ####
        # one 4 digit binary number per square on chessboard, mapping in dict below         256 bits
        # Castling rights: white king, white queen, black king, black queen                 4 bits
        # Player to move: 0 is white, 1 is black                                            1 bit
        #### Total bits: 301 bits
        
        # White is capitalized, black is lower case
        piece_mapping = {'P':'0001', 'R':'0010','N':'0011','B':'0100','Q':'0101','K':'0110','p':'1001', 'r':'1010','n':'1011','b':'1100','q':'1101','k':'1110'}

        bitboard = '0b'
        fen = self.fen()
        (board_state, turn, can_castle, en_passant, half_moves, move_count) = fen.split(' ')
        
        # Iterates through FEN notation converting into binary representation
        for square in board_state:
            # Skip the separaters
            if square == '/':
                continue
            # Check if the squares are empty
            elif square not in piece_mapping:
                bitboard += int(square) * '0000'
            else:
                bitboard += piece_mapping[square]

        # Checks whether black and white are able to castle then adds information to the bitboard
        can_castle = list(can_castle)
        white_king = '0'
        white_queen = '0'
        black_king = '0'
        black_queen = '0'
        if 'K' in can_castle:
            white_king = '1'
        if 'Q' in can_castle:
            white_queen = '1'
        if 'k' in can_castle:
            black_king = '1'
        if 'q' in can_castle:
            black_queen = '1'
        bitboard = bitboard + white_king + white_queen + black_king + black_queen

        # Adds whose turn it is to the end
        if turn =='b':
            bitboard += '1'
        else:
            bitboard += '0'

        return bitboard

    def get_move_list_fen(self):
        #Returns list of FEN for boards that can be moved to
        move_list = []
        for move in self.legal_moves:
            self.push(move)
            move_list.append(self.fen())
            self.pop()
        return move_list

    def basic_rating(self, mobility_weight=1, center_weight=2, material_weight=5):
        # Returns a number rating the quality of the board state for the person whose turn it is
        # Attempts to consider: average mobility of pieces, control of center, and material value
        # The higher the score the better off the player is
        # Returns 0 for a loss, proceeds as normal for a draw

        if self.is_checkmate():
            #If I've been checkmated, the reward is minus the largest value seen so far
            return -200

        mobility = 0
        center = 0
        material = 0    

        # Mobility of pieces
        mobility += self.legal_moves.count()

        #Control of center - number of pieces occupying center plus number of pieces attacking the center
        # The four center squares are D4, E4, D5, and E5
        center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
        for square in center_squares:
           center += len(self.attackers(self.turn, square))
           center_piece = self.piece_at(square)
           if center_piece and center_piece.color == self.turn:
               center += 1

        #Material Advantage
        # Rooks are 5, bishops and knights are 3, queen is 9, king is 4, pawns are 1
        piece_values = {chess.PAWN : 1, chess.BISHOP : 3, chess.KNIGHT : 3, chess.QUEEN : 9, chess.KING : 4, chess.PAWN : 1}
        my_material = 0
        their_material = 0
        for piece in piece_values:
            my_material += len(self.pieces(piece, self.turn)) * piece_values[piece]
            their_material += len(self.pieces(piece, not self.turn)) * piece_values[piece]
        material = my_material - their_material

        
        score = mobility * mobility_weight + center * center_weight + material * material_weight
        return score