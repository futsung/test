import pygame
import os
from board import Board
from utils import load_images, draw_enemy_health_bar, draw_status_bar

def show_start_screen(screen, background_image):
    """
    顯示遊戲的起始畫面，背景使用提供的圖片。
    """
    # 繪製背景圖片
    screen.blit(background_image, (0, 0))

    # 設置開始按鈕
    font_button = pygame.font.Font(None, 48)
    button_text = font_button.render("START", True, (0, 0, 0))
    button_rect = pygame.Rect(260, 400, 200, 80)

    # 繪製開始按鈕
    pygame.draw.rect(screen, (255, 255, 255), button_rect)
    screen.blit(button_text, (button_rect.centerx - button_text.get_width() // 2,
                              button_rect.centery - button_text.get_height() // 2))
    pygame.display.flip()

    # 等待玩家點擊按鈕
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    waiting = False

def show_summary(screen, traffic_tickets, images, y_offset=0):
    """
    顯示遊戲結束畫面，背景使用 victory.jpg，只顯示罰單數字，Y 方向可調整。
    :param screen: Pygame 畫布
    :param traffic_tickets: 罰單數字
    :param images: 圖片資源
    :param y_offset: Y 軸方向的偏移量，預設為 0
    """
    # 設定結算畫面背景
    screen.fill((0, 0, 0))  # 黑色背景
    screen.blit(images["victory"], (0, 0))  # 加載 victory.jpg 作為背景

    # 設定字體
    font = pygame.font.Font(None, 72)  # 字體大小設定為 72

    # 顯示罰單數字並調整 Y 軸位置
    text_number = font.render(f"{traffic_tickets}", True, (255, 255, 255))
    number_rect = text_number.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + y_offset))
    screen.blit(text_number, number_rect)

    # 更新畫面並停留 5 秒
    pygame.display.flip()
    pygame.time.wait(5000)

def main():
    """
    遊戲的主要邏輯與主迴圈。
    """
    # 遊戲參數
    SCREEN_WIDTH, SCREEN_HEIGHT = 720, 800
    ROWS, COLS = 5, 6
    TILE_SIZE = 100
    FPS = 60

    # 初始化 Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("行人地獄")  # 遊戲標題
    clock = pygame.time.Clock()

    # 加載圖片路徑
    base_dir = os.path.dirname(__file__)
    image_path = {
        "car": os.path.join(base_dir, "Image", "car.png"),
        "scooter": os.path.join(base_dir, "Image", "scooter.png"),
        "bus": os.path.join(base_dir, "Image", "bus.png"),
        "train": os.path.join(base_dir, "Image", "train.png"),
        "bike": os.path.join(base_dir, "Image", "bike.jpg"),
        "background": os.path.join(base_dir, "Image", "background.jpg"),
        "man": os.path.join(base_dir, "Image", "man.png"),
        "old_woman": os.path.join(base_dir, "Image", "old_woman.png"),
        "kid_and_dog": os.path.join(base_dir, "Image", "kid_and_dog.png"),
        "victory": os.path.join(base_dir, "Image", "victory.jpg"),
        "start_background": os.path.join(base_dir, "Image", "alivinghell.jpg")  # 初始畫面背景
    }

    # 加載圖片資源
    images = load_images(image_path, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT)

    # 加載初始畫面背景圖片
    start_background = pygame.image.load(image_path["start_background"])
    start_background = pygame.transform.scale(start_background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # 顯示起始畫面
    show_start_screen(screen, start_background)

    # 初始化遊戲板
    board = Board()

    # 敵人參數
    enemies = ["man", "old_woman", "kid_and_dog"]
    enemy_health = [150, 250, 500]
    enemy_sizes = [(150, 200), (250, 220), (150, 200)]
    current_enemy_index = 0
    max_health = enemy_health[current_enemy_index]
    health = max_health

    # 遊戲狀態參數
    traffic_tickets = 0
    combo = 0
    level = 1

    # 遊戲循環控制
    running = True
    dragging = False
    start_pos = None

    while running:
        screen.fill((0, 0, 0))
        screen.blit(images["background"], (0, 0))  # 顯示背景圖

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                start_pos = pygame.mouse.get_pos()
                dragging = True
                board.handle_drag(start_pos, start_pos)

            if event.type == pygame.MOUSEMOTION and dragging:
                board.continue_drag(pygame.mouse.get_pos())

            if event.type == pygame.MOUSEBUTTONUP:
                dragging = False
                board.end_drag()
                matches = board.check_matches()
                if matches:
                    combo += 1
                    damage = len(matches) * 10
                    health -= damage
                    traffic_tickets += damage
                    if health <= 0:
                        level += 1
                        if level > len(enemies):
                            show_summary(screen, traffic_tickets, images)
                            running = False
                        else:
                            current_enemy_index = level - 1
                            health = enemy_health[current_enemy_index]
                            max_health = health
                    board.apply_gravity()

        # 繪製敵人
        enemy_x = SCREEN_WIDTH // 2 - enemy_sizes[current_enemy_index][0] // 2
        enemy_y = 31
        enemy_image = pygame.transform.scale(images[enemies[current_enemy_index]], enemy_sizes[current_enemy_index])
        screen.blit(enemy_image, (enemy_x, enemy_y))
        draw_enemy_health_bar(screen, health, max_health, enemy_x, enemy_y - 20, enemy_sizes[current_enemy_index][0], 10)

        # 繪製遊戲盤面
        board.draw(screen, images)

        # 繪製狀態欄
        draw_status_bar(screen, traffic_tickets, combo, level)

        # 更新螢幕
        pygame.display.flip()
        clock.tick(FPS)

    # 結束遊戲
    pygame.quit()

if __name__ == "__main__":
    main()
