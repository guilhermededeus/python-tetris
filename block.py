from colors import Colors
import pygame
from position import Position

class Block:
	def __init__(self, id):
		self.id = id
		self.cells = {}
		self.cell_size = 30
		self.row_offset = 0
		self.column_offset = 0
		self.rotation_state = 0
		self.colors = Colors.get_cell_colors()

	def move(self, rows, columns):
		self.row_offset += rows
		self.column_offset += columns

	def get_cell_positions(self):
		tiles = self.cells[self.rotation_state]
		return [Position(p.row + self.row_offset, p.column + self.column_offset) for p in tiles]

	def rotate(self):
		self.rotation_state = (self.rotation_state + 1) % len(self.cells)

	def undo_rotation(self):
		self.rotation_state = (self.rotation_state - 1) % len(self.cells)

	def draw(self, screen, offset_x, offset_y):
		for tile in self.get_cell_positions():
			tile_rect = pygame.Rect(
				offset_x + tile.column * self.cell_size,
				offset_y + tile.row * self.cell_size,
				self.cell_size - 1,
				self.cell_size - 1
			)
			pygame.draw.rect(screen, self.colors[self.id], tile_rect)
