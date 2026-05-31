import os
import pygame
from grid import Grid
from blocks import *
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Game:
	def __init__(self):
		self.grid         = Grid()
		self.blocks       = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
		self.current_block = self.get_random_block()
		self.next_block    = self.get_random_block()
		self.game_over    = False
		self.score        = 0
		self.high_score   = 0
		self._load_high_score()

		self._pending_clear = False

		pygame.mixer.init()
		self.rotate_sound    = pygame.mixer.Sound(os.path.join(BASE_DIR, "Sounds", "rotate.ogg"))
		self.clear_sound     = pygame.mixer.Sound(os.path.join(BASE_DIR, "Sounds", "clear.ogg"))
		self.game_over_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "Sounds", "game_over.ogg"))

		pygame.mixer.music.load(os.path.join(BASE_DIR, "Sounds", "music_theme.ogg"))
		pygame.mixer.music.play(-1)

	def _hs_path(self):
		return os.path.join(BASE_DIR, "highscore.txt")

	def _load_high_score(self):
		try:
			with open(self._hs_path()) as f:
				self.high_score = int(f.read().strip())
		except Exception:
			self.high_score = 0

	def _save_high_score(self):
		try:
			with open(self._hs_path(), "w") as f:
				f.write(str(self.high_score))
		except Exception:
			pass

	def update_score(self, lines_cleared, move_down_points):
		table = {1: 100, 2: 300, 3: 500, 4: 800}
		self.score += table.get(lines_cleared, 0) + move_down_points
		if self.score > self.high_score:
			self.high_score = self.score
			self._save_high_score()

	def get_random_block(self):
		if not self.blocks:
			self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
		block = random.choice(self.blocks)
		self.blocks.remove(block)
		return block

	def move_left(self):
		self.current_block.move(0, -1)
		if not self.block_inside() or not self.block_fits():
			self.current_block.move(0, 1)

	def move_right(self):
		self.current_block.move(0, 1)
		if not self.block_inside() or not self.block_fits():
			self.current_block.move(0, -1)

	def move_down(self):
		self.current_block.move(1, 0)
		if not self.block_inside() or not self.block_fits():
			self.current_block.move(-1, 0)
			self.lock_block()

	def hard_drop(self):
		"""Drop the current block all the way down instantly."""
		cells_dropped = 0
		while True:
			self.current_block.move(1, 0)
			if not self.block_inside() or not self.block_fits():
				self.current_block.move(-1, 0)
				break
			cells_dropped += 1
		self.update_score(0, cells_dropped * 2)
		self.lock_block()

	def lock_block(self):
		for pos in self.current_block.get_cell_positions():
			self.grid.grid[pos.row][pos.column] = self.current_block.id
		self.current_block = self.next_block
		self.next_block    = self.get_random_block()

		full_rows = self.grid.find_full_rows()
		if full_rows:
			self.grid.flashing_rows = full_rows
			self.grid.flash_active  = True
			self.grid.flash_timer_ms = 0
			self._pending_clear = True
			self.clear_sound.play()
		else:
			self._check_game_over()

	def commit_clear(self):
		rows_cleared = self.grid.commit_clear_full_rows()
		self.update_score(rows_cleared, 0)
		self._pending_clear = False
		self._check_game_over()

	def _check_game_over(self):
		if not self.block_fits():
			self.game_over = True
			pygame.mixer.music.stop()
			self.game_over_sound.play()

	def update_flash(self, dt):
		if self._pending_clear:
			return self.grid.update_flash(dt)
		return False

	def block_fits(self):
		return all(self.grid.is_empty(t.row, t.column)
		           for t in self.current_block.get_cell_positions())

	def block_inside(self):
		return all(self.grid.is_inside(t.row, t.column)
		           for t in self.current_block.get_cell_positions())

	def rotate(self):
		self.current_block.rotate()
		if not self.block_inside() or not self.block_fits():
			self.current_block.undo_rotation()
		else:
			self.rotate_sound.play()

	def reset(self):
		self.grid.reset()
		self.blocks        = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
		self.current_block = self.get_random_block()
		self.next_block    = self.get_random_block()
		self.score         = 0
		self.game_over     = False
		self._pending_clear = False
		pygame.mixer.music.play(-1)

	def draw(self, screen, offset_x, offset_y):
		self.grid.draw(screen, offset_x, offset_y)
		if not self._pending_clear:
			self.current_block.draw(screen, offset_x + 11, offset_y + 11)

		if self.next_block.id == 3:
			self.next_block.draw(screen, offset_x + 255, offset_y + 290)
		elif self.next_block.id == 4:
			self.next_block.draw(screen, offset_x + 255, offset_y + 280)
		else:
			self.next_block.draw(screen, offset_x + 270, offset_y + 270)
