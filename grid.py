import pygame
from colors import Colors

FLASH_DURATION_MS = 300
FLASH_FRAMES      = 4     

class Grid:
	def __init__(self):
		self.num_rows  = 20
		self.num_cols  = 10
		self.cell_size = 30
		self.grid      = [[0] * self.num_cols for _ in range(self.num_rows)]
		self.colors    = Colors.get_cell_colors()

		self.flashing_rows  = []  
		self.flash_timer_ms = 0   
		self.flash_active   = False

	def is_inside(self, row, column):
		return 0 <= row < self.num_rows and 0 <= column < self.num_cols

	def is_empty(self, row, column):
		return self.grid[row][column] == 0

	def is_row_full(self, row):
		return all(self.grid[row][col] != 0 for col in range(self.num_cols))

	def clear_row(self, row):
		self.grid[row] = [0] * self.num_cols

	def move_row_down(self, row, num_rows):
		self.grid[row + num_rows] = self.grid[row][:]
		self.grid[row] = [0] * self.num_cols

	def find_full_rows(self):
		return [r for r in range(self.num_rows) if self.is_row_full(r)]

	def commit_clear_full_rows(self):
		"""Actually remove the flashing rows and collapse the grid. Returns count."""
		completed = 0
		for row in range(self.num_rows - 1, 0, -1):
			if self.is_row_full(row):
				self.clear_row(row)
				completed += 1
			elif completed > 0:
				self.move_row_down(row, completed)
		self.flashing_rows = []
		self.flash_active  = False
		self.flash_timer_ms = 0
		return completed

	def reset(self):
		self.grid = [[0] * self.num_cols for _ in range(self.num_rows)]
		self.flashing_rows  = []
		self.flash_active   = False
		self.flash_timer_ms = 0

	def update_flash(self, dt):
		"""Returns True when animation is done and rows should be cleared."""
		if not self.flash_active:
			return False
		self.flash_timer_ms += dt
		if self.flash_timer_ms >= FLASH_DURATION_MS:
			return True
		return False

	def _flash_visible(self):
		"""Alternates on/off based on elapsed time."""
		phase = int(self.flash_timer_ms / (FLASH_DURATION_MS / (FLASH_FRAMES * 2)))
		return (phase % 2) == 0
	
	def draw(self, screen, offset_x, offset_y):
		flash_on = self._flash_visible()
		for row in range(self.num_rows):
			for column in range(self.num_cols):
				cell_value = self.grid[row][column]
				cell_rect  = pygame.Rect(
					offset_x + column * self.cell_size + 11,
					offset_y + row    * self.cell_size + 11,
					self.cell_size - 1,
					self.cell_size - 1
				)
				if row in self.flashing_rows:
					color = Colors.white if flash_on else Colors.dark_grey
				else:
					color = self.colors[cell_value]
				pygame.draw.rect(screen, color, cell_rect)
