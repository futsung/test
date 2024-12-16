import random
import pygame 
from models import Runestone
from stone_types import StoneType

class Board:
    def __init__(self):
         # 初始化遊戲盤面參數
        self.rows = 5 # 行數
        self.cols = 6 # 列數
        self.tile_size = 100 # 每個格子的大小
        self.tiles = self.generate_board() # 生成初始遊戲盤面
        self.selected = None
        self.dragging = False
        self.drag_tile = None
        self.drag_path = [] # 儲存拖曳路徑

    def generate_board(self):
        """
        生成一個隨機的遊戲盤面，保證沒有初始消除的情況。
        """
        while True:
            tiles = [[Runestone(random.choice(list(StoneType))) for _ in range(self.cols)] for _ in range(self.rows)]
            if not self.has_initial_matches(tiles):
                return tiles

    def has_initial_matches(self, tiles):
        """
        檢查是否存在初始的三消匹配。
        """
        for row in range(self.rows):
            for col in range(self.cols - 2):
                if (
                    tiles[row][col].type == tiles[row][col + 1].type == tiles[row][col + 2].type
                ):
                    return True
        for col in range(self.cols):
            for row in range(self.rows - 2):
                if (
                    tiles[row][col].type == tiles[row + 1][col].type == tiles[row + 2][col].type
                ):
                    return True
        return False

    def draw(self, screen, images):
        """
        繪製遊戲盤面。
        """
        for row in range(self.rows):
            for col in range(self.cols):
                tile = self.tiles[row][col]
                if tile:
                    x, y = col * self.tile_size + 50, row * self.tile_size + 300
                    screen.blit(images[tile.type.value], (x, y))
                    pygame.draw.rect(screen, (255, 255, 255), (x, y, self.tile_size, self.tile_size), 1)

    def handle_drag(self, start_pos, end_pos):
        """
        處理玩家的拖曳起始點。
        """
        start_x, start_y = start_pos
        start_col, start_row = (start_x - 50) // self.tile_size, (start_y - 300) // self.tile_size

        if not (0 <= start_row < self.rows and 0 <= start_col < self.cols):
            print(f"起始座標超出範圍：({start_row}, {start_col})")
            return

        self.drag_path.append((start_row, start_col))

    def continue_drag(self, current_pos):
        """
        處理拖曳中的移動，交換兩個格子的內容。
        """
        current_x, current_y = current_pos
        current_col, current_row = (current_x - 50) // self.tile_size, (current_y - 300) // self.tile_size

        if not (0 <= current_row < self.rows and 0 <= current_col < self.cols):
            return

        if self.drag_path and self.drag_path[-1] != (current_row, current_col):
            last_row, last_col = self.drag_path[-1]
            self.tiles[last_row][last_col], self.tiles[current_row][current_col] = (
                self.tiles[current_row][current_col],
                self.tiles[last_row][last_col],
            )
            self.drag_path.append((current_row, current_col))

    def end_drag(self):
        """
        清空拖曳路徑。
        """
        self.drag_path = []

    def apply_gravity(self):
        for col in range(self.cols):
            for row in range(self.rows - 1, -1, -1):
                if not self.tiles[row][col]:
                    for upper_row in range(row - 1, -1, -1):
                        if self.tiles[upper_row][col]:
                            self.tiles[row][col], self.tiles[upper_row][col] = self.tiles[upper_row][col], None
                            break
                    if not self.tiles[row][col]:
                        self.tiles[row][col] = Runestone(random.choice(list(StoneType)))

    def check_matches(self):
        """
        檢查盤面上的三消匹配，並移除匹配的格子。
        """
        matched = set()
        for row in range(self.rows):
            for col in range(self.cols - 2):
                if (
                    self.tiles[row][col] and
                    self.tiles[row][col + 1] and
                    self.tiles[row][col + 2] and
                    self.tiles[row][col].type == self.tiles[row][col + 1].type == self.tiles[row][col + 2].type
                ):
                    matched.add((row, col))
                    matched.add((row, col + 1))
                    matched.add((row, col + 2))
        for col in range(self.cols):
            for row in range(self.rows - 2):
                if (
                    self.tiles[row][col] and
                    self.tiles[row + 1][col] and
                    self.tiles[row + 2][col] and
                    self.tiles[row][col].type == self.tiles[row + 1][col].type == self.tiles[row + 2][col].type
                ):
                    matched.add((row, col))
                    matched.add((row + 1, col))
                    matched.add((row + 2, col))
        # 將匹配的格子清空
        for (row, col) in matched:
            if self.tiles[row][col]:
                self.tiles[row][col] = None

        return matched



