import sqlite3

class UCTChessDB:
	def __init__(self, db_name='chessv1.db', db_table='ChessTable'):
		self.db_name = db_name
		self.conn = None
		self.cursor = None
		self.current_table = db_table
		self.read_only = True

	def initialize_table(self, name='ChessTable'):
		self.cursor.execute(f'CREATE TABLE IF NOT EXISTS {name} (FEN TEXT PRIMARY KEY, Visits INTEGER, TotalValue INTEGER)')

	def set_current_table(self, name):
		self.current_table = name
		self.initialize_table(name=name)
		
	def get_value(self, fen):
		value = self._get_value(fen)
		if value is None:
			return None
		(visits, total_value) = value
		return total_value / visits

	def _get_value(self, fen):
		self.cursor.execute(f'SELECT Visits, TotalValue FROM {self.current_table} WHERE FEN=?', (fen,))
		return self.cursor.fetchone()

	def set_value(self, fen, visits, total_reward):
		value = self._get_value(fen)
		if value is None:
			self.cursor.execute(f'INSERT INTO {self.current_table} VALUES (?, ?, ?)', (fen, visits, total_reward))
		else:
			(old_visits, old_reward) = value
			visits = visits + old_visits
			total_reward = total_reward + old_reward
			self.cursor.execute(f'UPDATE {self.current_table} SET Visits = ?, TotalValue = ? WHERE FEN = ?', (visits, total_reward, fen))

	def close_db(self):
		if not self.read_only:
			self.commit_changes()
			self.read_only = True

		if self.cursor:
			self.cursor.close()
			self.cursor = None
		if self.conn:
			self.conn.close()
			self.conn = None

	def open_db(self, read_only=True):
		self.read_only = read_only
		if read_only:
			self.conn = sqlite3.connect('file:' + self.db_name + '?mode=ro', uri=True)
			#self.conn = sqlite3.connect('D:\\SharedFolder\\Programs\\Python\\UCTChess\\chessv1.db')
		else:
			self.conn = sqlite3.connect(self.db_name)

		self.cursor = self.conn.cursor()

	def commit_changes(self):
		self.conn.commit()