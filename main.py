import pygame,sys
from game import Game
from colors import Colors

GAME_W, GAME_H   = 500, 620
FPS              = 60
BASE_INTERVAL    = 500
MIN_INTERVAL     = 80
POINTS_PER_LEVEL = 500

pygame.init()
pygame.mixer.init()

screen     = pygame.display.set_mode((GAME_W, GAME_H), pygame.RESIZABLE)
pygame.display.set_caption("Python Tetris")
clock      = pygame.time.Clock()
canvas     = pygame.Surface((GAME_W, GAME_H))
fullscreen = False

title_font = pygame.font.Font(None, 40)
label_font = pygame.font.Font(None, 32)
big_font   = pygame.font.Font(None, 52)
btn_font   = pygame.font.Font(None, 38)
small_font = pygame.font.Font(None, 28)

game  = Game()
state = "menu"

GAME_UPDATE      = pygame.USEREVENT
current_interval = BASE_INTERVAL
pygame.time.set_timer(GAME_UPDATE, current_interval)

def draw_button(surf, text, center, w, h, bg, fg, radius=12):
	rect = pygame.Rect(0, 0, w, h)
	rect.center = center
	pygame.draw.rect(surf, bg, rect, border_radius=radius)
	label = btn_font.render(text, True, fg)
	surf.blit(label, label.get_rect(center=rect.center))
	return rect

def blit_canvas(dest, src):
	sw, sh = dest.get_size()
	scale  = min(sw / GAME_W, sh / GAME_H)
	nw, nh = int(GAME_W * scale), int(GAME_H * scale)
	scaled = pygame.transform.smoothscale(src, (nw, nh))
	dest.fill(Colors.black)
	dest.blit(scaled, ((sw - nw) // 2, (sh - nh) // 2))
	return scale, (sw - nw) // 2, (sh - nh) // 2

def canvas_mouse_pos(event_pos):
	sw, sh   = screen.get_size()
	s        = min(sw / GAME_W, sh / GAME_H)
	nw, nh   = int(GAME_W * s), int(GAME_H * s)
	ox, oy   = (sw - nw) // 2, (sh - nh) // 2
	return ((event_pos[0] - ox) / s, (event_pos[1] - oy) / s)

def level_from_score(score):
	return min(score // POINTS_PER_LEVEL + 1, 10)

def interval_from_level(level):
	t = (level - 1) / 9.0
	return int(BASE_INTERVAL + (MIN_INTERVAL - BASE_INTERVAL) * t)

def update_speed():
	global current_interval
	new = interval_from_level(level_from_score(game.score))
	if new != current_interval:
		current_interval = new
		pygame.time.set_timer(GAME_UPDATE, current_interval)

def start_game():
	global state, current_interval
	game.reset()
	current_interval = BASE_INTERVAL
	pygame.time.set_timer(GAME_UPDATE, current_interval)
	state = "playing"

def toggle_pause():
	global state
	if state == "playing":
		state = "paused"
		pygame.mixer.music.pause()
		pygame.time.set_timer(GAME_UPDATE, 0)     
	elif state == "paused":
		state = "playing"
		pygame.mixer.music.unpause()
		pygame.time.set_timer(GAME_UPDATE, current_interval)


PANEL_X     = 320
record_rect = pygame.Rect(PANEL_X, 15,  170, 55)
score_rect  = pygame.Rect(PANEL_X, 95,  170, 55)
level_rect  = pygame.Rect(PANEL_X, 165, 170, 45)
next_rect   = pygame.Rect(PANEL_X, 225, 170, 180)

running = True
while running:
	dt = clock.tick(FPS)  

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
			fullscreen = not fullscreen
			if fullscreen:
				screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
			else:
				screen = pygame.display.set_mode((GAME_W, GAME_H), pygame.RESIZABLE)

		elif state == "menu":
			if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
				start_game()
			elif event.type == pygame.MOUSEBUTTONDOWN:
				cm = canvas_mouse_pos(event.pos)
				btn = pygame.Rect(0, 0, 200, 55); btn.center = (GAME_W // 2, GAME_H // 2 + 60)
				if btn.collidepoint(cm):
					start_game()

		elif state == "playing":
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					toggle_pause()
				elif not game._pending_clear: 
					if event.key in (pygame.K_LEFT,  pygame.K_a):   game.move_left()
					elif event.key in (pygame.K_RIGHT, pygame.K_d): game.move_right()
					elif event.key in (pygame.K_DOWN,  pygame.K_s):
						game.move_down(); game.update_score(0, 1)
					elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_SPACE):
						game.rotate()
					elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
						game.hard_drop()

			elif event.type == GAME_UPDATE and not game._pending_clear:
				game.move_down()
				update_speed()

			if game.game_over:
				state = "gameover"

		elif state == "paused":
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					toggle_pause()
			elif event.type == pygame.MOUSEBUTTONDOWN:
				cm = canvas_mouse_pos(event.pos)
				resume_btn = pygame.Rect(0, 0, 180, 52); resume_btn.center = (GAME_W // 2, GAME_H // 2 + 10)
				quit_btn   = pygame.Rect(0, 0, 180, 52); quit_btn.center   = (GAME_W // 2, GAME_H // 2 + 75)
				if resume_btn.collidepoint(cm):
					toggle_pause()
				elif quit_btn.collidepoint(cm):
					running = False

		elif state == "gameover":
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RETURN:   start_game()
				elif event.key == pygame.K_ESCAPE: running = False
			elif event.type == pygame.MOUSEBUTTONDOWN:
				cm = canvas_mouse_pos(event.pos)
				cy = GAME_H // 2
				play_btn = pygame.Rect(0, 0, 160, 50); play_btn.center = (GAME_W // 2 - 90, cy + 40)
				exit_btn = pygame.Rect(0, 0, 160, 50); exit_btn.center = (GAME_W // 2 + 90, cy + 40)
				if play_btn.collidepoint(cm):   start_game()
				elif exit_btn.collidepoint(cm): running = False

	if state == "playing" and game.update_flash(dt):
		game.commit_clear()
		update_speed()
		if game.game_over:
			state = "gameover"

	canvas.fill(Colors.dark_blue)

	if state == "menu":
		big_title = pygame.font.Font(None, 80).render("TETRIS", True, Colors.cyan)
		canvas.blit(big_title, big_title.get_rect(center=(GAME_W // 2, GAME_H // 2 - 80)))
		sub = small_font.render("Press SPACE or click to start", True, Colors.white)
		canvas.blit(sub, sub.get_rect(center=(GAME_W // 2, GAME_H // 2 + 10)))
		draw_button(canvas, "Start Game", (GAME_W // 2, GAME_H // 2 + 60), 200, 55, Colors.green, Colors.black)
		hint = small_font.render("F11 = fullscreen", True, Colors.light_blue)
		canvas.blit(hint, hint.get_rect(center=(GAME_W // 2, GAME_H - 30)))

	else:
		level = level_from_score(game.score)

		for r in (record_rect, score_rect, level_rect, next_rect):
			pygame.draw.rect(canvas, Colors.light_blue, r, 0, 10)

		canvas.blit(label_font.render("Record", True, Colors.gold),
		            label_font.render("Record", True, Colors.gold).get_rect(
		                centerx=record_rect.centerx, top=record_rect.top + 4))
		canvas.blit(title_font.render(str(game.high_score), True, Colors.white),
		            title_font.render(str(game.high_score), True, Colors.white).get_rect(
		                centerx=record_rect.centerx, bottom=record_rect.bottom - 4))

		canvas.blit(label_font.render("Score", True, Colors.white),
		            label_font.render("Score", True, Colors.white).get_rect(
		                centerx=score_rect.centerx, top=score_rect.top + 4))
		canvas.blit(title_font.render(str(game.score), True, Colors.white),
		            title_font.render(str(game.score), True, Colors.white).get_rect(
		                centerx=score_rect.centerx, bottom=score_rect.bottom - 4))

		canvas.blit(small_font.render(f"Level  {level}", True, Colors.white),
		            small_font.render(f"Level  {level}", True, Colors.white).get_rect(
		                center=level_rect.center))

		canvas.blit(label_font.render("Next", True, Colors.white),
		            label_font.render("Next", True, Colors.white).get_rect(
		                centerx=next_rect.centerx, top=next_rect.top + 6))

		game.draw(canvas, 0, 0)

		if state == "paused":
			overlay = pygame.Surface((GAME_W, GAME_H), pygame.SRCALPHA)
			overlay.fill((0, 0, 0, 180))
			canvas.blit(overlay, (0, 0))

			cy = GAME_H // 2
			pause_surf = big_font.render("PAUSED", True, Colors.white)
			canvas.blit(pause_surf, pause_surf.get_rect(center=(GAME_W // 2, cy - 50)))

			draw_button(canvas, "Resume",   (GAME_W // 2, cy + 10),  180, 52, Colors.green, Colors.black)
			draw_button(canvas, "Quit",     (GAME_W // 2, cy + 75),  180, 52, Colors.red,   Colors.white)

			hint = small_font.render("Esc = resume", True, Colors.light_blue)
			canvas.blit(hint, hint.get_rect(center=(GAME_W // 2, cy + 130)))

		elif state == "gameover":
			overlay = pygame.Surface((GAME_W, GAME_H), pygame.SRCALPHA)
			overlay.fill((0, 0, 0, 170))
			canvas.blit(overlay, (0, 0))

			cy = GAME_H // 2
			canvas.blit(big_font.render("GAME OVER", True, Colors.white),
			            big_font.render("GAME OVER", True, Colors.white).get_rect(
			                center=(GAME_W // 2, cy - 60)))
			canvas.blit(label_font.render(f"Score: {game.score}   Level: {level}", True, Colors.gold),
			            label_font.render(f"Score: {game.score}   Level: {level}", True, Colors.gold).get_rect(
			                center=(GAME_W // 2, cy - 10)))

			draw_button(canvas, "Play Again", (GAME_W // 2 - 90, cy + 40), 160, 50, Colors.green, Colors.black)
			draw_button(canvas, "Exit",       (GAME_W // 2 + 90, cy + 40), 160, 50, Colors.red,   Colors.white)

			hint = small_font.render("Enter = play again   Esc = exit", True, Colors.light_blue)
			canvas.blit(hint, hint.get_rect(center=(GAME_W // 2, cy + 105)))

	blit_canvas(screen, canvas)
	pygame.display.update()

pygame.quit()
sys.exit()
