import pygame
import random
import math

pygame.init()


FPS = 60
WIDTH, HEIGHT = 700, 700
ROWS, COLS = 4, 4
RECT_HEIGHT = HEIGHT // ROWS
RECT_WIDTH = WIDTH // COLS
OUTLINE_COLOR = (187, 173, 160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (205, 192, 180)
FONT_COLOR = (119, 110, 101)
FONT = pygame.font.SysFont("comicsans", 60, bold=True)
MOVE_VEL = 20

class Tile:
    COLORS = [
        (237, 229, 218),
        (238, 225, 201),
        (243, 178, 122),
        (246, 150, 101),
        (247, 124, 95),
        (247, 95, 59),
        (237, 208, 115),
        (237, 204, 99),
        (236, 202, 80),
        (235, 200, 61),
    ]

    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.target_row = row
        self.target_col = col
        self.x = col * RECT_WIDTH
        self.y = row * RECT_HEIGHT

    def get_color(self):
        try:
            color_index = int(math.log2(self.value)) - 1
            return self.COLORS[color_index]
        except (IndexError, ValueError):
            return self.COLORS[0]  

    def draw(self, window):
        color = self.get_color()
        pygame.draw.rect(window, color, (self.x, self.y, RECT_WIDTH, RECT_HEIGHT))
        text = FONT.render(str(self.value), 1, FONT_COLOR)
        window.blit(text, (self.x + (RECT_WIDTH - text.get_width()) / 2,
                           self.y + (RECT_HEIGHT - text.get_height()) / 2))

    def update_position(self):
        if self.x != self.target_col * RECT_WIDTH:
            self.x += MOVE_VEL if self.x < self.target_col * RECT_WIDTH else -MOVE_VEL
        if self.y != self.target_row * RECT_HEIGHT:
            self.y += MOVE_VEL if self.y < self.target_row * RECT_HEIGHT else -MOVE_VEL
        self.x = min(max(self.x, self.target_col * RECT_WIDTH), self.target_col * RECT_WIDTH)
        self.y = min(max(self.y, self.target_row * RECT_HEIGHT), self.target_row * RECT_HEIGHT)

class GameBoard:
    def __init__(self):
        self.tiles = {}
        self.generate_tiles()

    def generate_tiles(self):
        try:
            for _ in range(2):
                pos = self.get_random_pos()
                if pos:
                    row, col = pos
                    self.tiles[f"{row}{col}"] = Tile(2, row, col)
        except Exception as e:
            print(f"Error generating tiles: {e}")

    def get_random_pos(self):
        empty_positions = [(r, c) for r in range(ROWS) for c in range(COLS) if f"{r}{c}" not in self.tiles]
        if not empty_positions:
            return None
        return random.choice(empty_positions)

    def slide_and_merge(self, direction):
        def slide_line(line):
            new_line = [tile for tile in line if tile != 0]
            for i in range(1, len(new_line)):
                if new_line[i] == new_line[i - 1]:
                    new_line[i - 1] *= 2
                    new_line[i] = 0
            new_line = [tile for tile in new_line if tile != 0]
            return new_line + [0] * (COLS - len(new_line))

        try:
            if direction in ["left", "right"]:
                for r in range(ROWS):
                    row = [self.tiles.get(f"{r}{c}", 0).value if f"{r}{c}" in self.tiles else 0 for c in range(COLS)]
                    if direction == "right":
                        row = row[::-1]
                    new_row = slide_line(row)
                    if direction == "right":
                        new_row = new_row[::-1]
                    for c in range(COLS):
                        key = f"{r}{c}"
                        if new_row[c] != 0:
                            if key in self.tiles:
                                self.tiles[key].value = new_row[c]
                                self.tiles[key].target_row = r
                                self.tiles[key].target_col = c
                            else:
                                self.tiles[key] = Tile(new_row[c], r, c)
                        elif key in self.tiles:
                            del self.tiles[key]

            elif direction in ["up", "down"]:
                for c in range(COLS):
                    col = [self.tiles.get(f"{r}{c}", 0).value if f"{r}{c}" in self.tiles else 0 for r in range(ROWS)]
                    if direction == "down":
                        col = col[::-1]
                    new_col = slide_line(col)
                    if direction == "down":
                        new_col = new_col[::-1]
                    for r in range(ROWS):
                        key = f"{r}{c}"
                        if new_col[r] != 0:
                            if key in self.tiles:
                                self.tiles[key].value = new_col[r]
                                self.tiles[key].target_row = r
                                self.tiles[key].target_col = c
                            else:
                                self.tiles[key] = Tile(new_col[r], r, c)
                        elif key in self.tiles:
                            del self.tiles[key]
        except Exception as e:
            print(f"Error sliding and merging tiles: {e}")

class Game:
    def __init__(self):
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("2048")
        self.clock = pygame.time.Clock()
        self.board = GameBoard()

    def draw_grid(self):
        for row in range(1, ROWS):
            y = row * RECT_HEIGHT
            pygame.draw.line(self.window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)
        for col in range(1, COLS):
            x = col * RECT_WIDTH
            pygame.draw.line(self.window, OUTLINE_COLOR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)
        pygame.draw.rect(self.window, OUTLINE_COLOR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS)

    def draw(self):
        self.window.fill(BACKGROUND_COLOR)
        for tile in self.board.tiles.values():
            tile.draw(self.window)
        self.draw_grid()
        pygame.display.update()

    def game_over(self):
        self.window.fill(BACKGROUND_COLOR)
        text = FONT.render("Game Over", 1, FONT_COLOR)
        self.window.blit(text, ((WIDTH - text.get_width()) / 2, (HEIGHT - text.get_height()) / 2))
        pygame.display.update()
        pygame.time.delay(3000)

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    direction = None
                    if event.key == pygame.K_LEFT:
                        direction = "left"
                    elif event.key == pygame.K_RIGHT:
                        direction = "right"
                    elif event.key == pygame.K_UP:
                        direction = "up"
                    elif event.key == pygame.K_DOWN:
                        direction = "down"
                    if direction:
                        try:
                            self.board.slide_and_merge(direction)
                            pos = self.board.get_random_pos()
                            if pos:
                                row, col = pos
                                self.board.tiles[f"{row}{col}"] = Tile(random.choice([2, 4]), row, col)
                            else:
                                self.game_over()
                                running = False
                        except Exception as e:
                            print(f"Error during game update: {e}")

            for tile in self.board.tiles.values():
                tile.update_position()

            self.draw()

        pygame.quit()

if __name__ == "__main__":
    Game().run()
