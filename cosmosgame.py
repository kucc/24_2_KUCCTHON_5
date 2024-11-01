import pygame
import random
import math

# 초기 설정
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("COSMOS GAME")

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
ORANGE = (255, 127, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
NAVY = (75, 0, 130)
PURPLE = (143, 0, 255)

# 폰트 설정
font = pygame.font.Font("game_font_1.ttf", 28)

# 게임 변수
clock = pygame.time.Clock()
score = 0
highscore = 0
scroll_speed = 5
max_scroll_speed = 10
speed_increase_interval = 5000
lives = 3
max_lives = 5

# 레벨 시스템 추가
level = 1
level_up_score_threshold = 100

# 배경 이미지 로드 및 크기 설정
background_image = pygame.image.load("background1.png")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# 무적 상태 변수
invincible = False
invincible_start_time = 0

# 무적 상태 지속 시간 (2초)
INVINCIBLE_DURATION = 2000  # milliseconds

# 로켓 설정
rocket_image = pygame.image.load("rocket.png")
rocket_image = pygame.transform.scale(rocket_image, (50, 50))
rocket_pos = [WIDTH // 2, HEIGHT // 2]
rocket_angle = 0
original_rocket_image = rocket_image

# 하트 이미지 로드 및 크기 설정
heart_image = pygame.image.load("heart.png")
heart_image = pygame.transform.scale(heart_image, (30, 30))

# 먼지 이미지 로드 및 크기 설정
dust_image = pygame.image.load("star.png")
dust_image = pygame.transform.scale(dust_image, (15, 15))

# 장애물 및 먼지 리스트
dusts = []
obstacles = []
blackholes = []
extra_lives = []

# 장애물 이미지 로드
rock_image = pygame.image.load("rock_obstacle.png")
rock_image = pygame.transform.scale(rock_image, (40, 40))

# 블랙홀 이미지 로드
blackhole_image = pygame.image.load("black.png")
blackhole_image = pygame.transform.scale(blackhole_image, (80, 80))

# 파이어볼 이미지 로드
fireball_image = pygame.image.load("fire.png")
fireball_image = pygame.transform.scale(fireball_image, (20, 20))

# 파이어볼 리스트
fireballs = []
fireball_spawn_interval = 7000
last_fireball_time = 0

# 각 운석의 회전 각도와 회전 속도 리스트
obstacle_angles = [0] * 5
obstacle_speeds = [random.randint(1, 10) for _ in range(5)]

# 상태 변수
paused = False
game_started = False
game_over = False

# 초기 화면 표시 함수
def show_start_screen():
    screen.fill(BLACK)
    title_text = font.render("Cosmos Game", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 100))
    
    # Start 버튼
    start_button = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2, 100, 40)
    pygame.draw.rect(screen, BLUE, start_button)
    start_text = font.render("Start", True, WHITE)
    screen.blit(start_text, (start_button.x + 10, start_button.y + 5))

    # Exit 버튼
    exit_button = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 60, 100, 40)
    pygame.draw.rect(screen, RED, exit_button)
    exit_text = font.render("Exit", True, WHITE)
    screen.blit(exit_text, (exit_button.x + 15, exit_button.y + 5))

    pygame.display.flip()
    return start_button, exit_button
    
# 먼지 및 장애물 생성 함수
def create_dust():
    x = random.randint(0, WIDTH)
    y = random.randint(-HEIGHT, 0)
    return pygame.Rect(x, y, 15, 15)

def create_obstacle():
    x = random.randint(0, WIDTH)
    y = random.randint(-HEIGHT, 0)
    return pygame.Rect(x, y, 40, 40)

def create_blackhole():
    x = random.randint(0, WIDTH)
    y = random.randint(-HEIGHT, 0)
    return pygame.Rect(x, y, 80, 80)

def create_extra_life():
    x = random.randint(0, WIDTH - 30)
    y = random.randint(-HEIGHT, 0)
    return pygame.Rect(x, y, 30, 30)

# 파이어볼 생성 함수
def create_fireballs():
    # 레벨에 따라 생성할 파이어볼 개수 설정
    fireball_count = 4 + (level - 4) // 3  # 4단계부터 4개, 이후 3레벨마다 1개씩 증가
    fireballs.clear()  # 기존 파이어볼 제거 후 새로 생성

    for _ in range(fireball_count):
        # 파이어볼이 화면 상단의 임의의 구간에서 생성되도록 설정
        x = random.randint(0, WIDTH)  # 화면 너비 내 임의의 x 위치
        y = random.randint(-100, 0)  # 화면 상단에서 조금 위쪽에서 생성
        direction_x = rocket_pos[0] - x
        direction_y = rocket_pos[1] - y
        distance = math.hypot(direction_x, direction_y)
        
        speed = 8  # 파이어볼 속도
        velocity_x = (direction_x / distance) * speed
        velocity_y = (direction_y / distance) * speed

        # 파이어볼 속도와 생성 위치를 fireballs 리스트에 추가
        fireballs.append({
            "rect": pygame.Rect(x, y, 20, 20),
            "velocity": (velocity_x, velocity_y)
        })

# 픽셀 충돌 체크 함수
def check_pixel_collision(obstacle):
    rotated_rocket_rect = rocket_image.get_rect(center=(rocket_pos[0], rocket_pos[1]))
    obstacle_rect = rock_image.get_rect(center=(obstacle.x, obstacle.y))
    rocket_mask = pygame.mask.from_surface(rocket_image)
    obstacle_mask = pygame.mask.from_surface(rock_image)
    offset = (obstacle_rect.x - rotated_rocket_rect.x, obstacle_rect.y - rotated_rocket_rect.y)
    collision_point = rocket_mask.overlap(obstacle_mask, offset)
    return collision_point is not None

# 함수 예시: 무적 상태 관리 함수
def handle_invincibility():
    global invincible, invincible_start_time
    # 무적 상태가 켜진 경우
    if invincible:
        invincible_text = font.render("Invincible!", True, YELLOW)
        screen.blit(invincible_text, (rocket_pos[0] - invincible_text.get_width() // 2, rocket_pos[1] - 40))
        if pygame.time.get_ticks() - invincible_start_time > INVINCIBLE_DURATION:
            invincible = False  # 무적 해제

# 로켓 렌더링 함수 - 색상 변경 효과 포함
def render_rocket():
    if invincible:
        pygame.draw.circle(screen, YELLOW, (rocket_pos[0], rocket_pos[1]), 30, 3)

# 충돌 체크 함수
def check_collisions():
    global score, lives, game_over, invincible, invincible_start_time
    for dust in dusts[:]:
        if math.hypot(rocket_pos[0] - dust.x, rocket_pos[1] - dust.y) < 25:
            score += 10
            dusts.remove(dust)
            dusts.append(create_dust())

    # 무적 상태가 아닐 때만 충돌 검사
    if not invincible:
        for i, obstacle in enumerate(obstacles):
            if check_pixel_collision(obstacle):
                lives -= 1
                obstacles.remove(obstacle)
                obstacles.append(create_obstacle())
                obstacle_angles.pop(i)
                obstacle_speeds.pop(i)
                obstacle_angles.append(0)
                obstacle_speeds.append(random.randint(1, 10))
                if lives <= 0:
                    game_over = True
                    break
                # 무적 상태 시작
                render_rocket()
                invincible = True
                invincible_start_time = pygame.time.get_ticks()           
                return False
    return True

# 블랙홀 흡입 함수
def check_blackhole_collision():
    global rocket_pos, rocket_angle, game_over
    for blackhole in blackholes:
        distance = math.hypot(rocket_pos[0] - blackhole.centerx, rocket_pos[1] - blackhole.centery)
        if distance < 100:
            direction_x = blackhole.centerx - rocket_pos[0]
            direction_y = blackhole.centery - rocket_pos[1]
            angle = math.atan2(direction_y, direction_x)
            rocket_pos[0] += math.cos(angle) * 3
            rocket_pos[1] += math.sin(angle) * 3
            rocket_angle += 10
            if distance < 20:
                game_over = True

# 초기 먼지 및 장애물 생성
for _ in range(10):
    dusts.append(create_dust())
for _ in range(5):
    obstacles.append(create_obstacle())
for _ in range(2):
    blackholes.append(create_blackhole())

# 게임 초기화 함수
def reset_game():
    global score, level, lives, scroll_speed, game_over, fireballs, obstacles, dusts, blackholes, extra_lives, rocket_pos, obstacle_angles, obstacle_speeds
    global highscore
    score = 0
    level = 1
    lives = 3
    scroll_speed = 5
    blackholes = [create_blackhole() for _ in range(2)]
    obstacles = [create_obstacle() for _ in range(5)]
    dusts = [create_dust() for _ in range(10)]
    rocket_pos = [WIDTH // 2, HEIGHT // 2]
    obstacle_angles = [0] * len(obstacles)
    obstacle_speeds = [random.randint(1, 10) for _ in range(len(obstacles))]
    extra_lives.clear()
    fireballs.clear()
    game_over = False

# 로켓 이동 함수
def move_rocket(keys):
    global rocket_image, rocket_angle
    if keys[pygame.K_a]: rocket_angle = 45
    elif keys[pygame.K_d]: rocket_angle = -45
    else: rocket_angle = 0
    rocket_image = pygame.transform.rotate(original_rocket_image, rocket_angle)
    if keys[pygame.K_w]: rocket_pos[1] -= 5
    if keys[pygame.K_s]: rocket_pos[1] += 5
    if keys[pygame.K_a]: rocket_pos[0] -= 5
    if keys[pygame.K_d]: rocket_pos[0] += 5
    rocket_pos[0] = max(0, min(WIDTH, rocket_pos[0]))
    rocket_pos[1] = max(0, min(HEIGHT, rocket_pos[1]))

# 파이어볼 이동 및 반사 처리 함수
def move_fireballs():
    global lives
    for fireball in fireballs[:]:
        fireball["rect"].x += fireball["velocity"][0]
        fireball["rect"].y += fireball["velocity"][1]
        if fireball["rect"].x <= 0 or fireball["rect"].x >= WIDTH - fireball["rect"].width:
            fireball["velocity"] = (-fireball["velocity"][0], fireball["velocity"][1])
        if fireball["rect"].y >= HEIGHT:
            fireballs.remove(fireball)
            continue
        if math.hypot(rocket_pos[0] - fireball["rect"].centerx, rocket_pos[1] - fireball["rect"].centery) < 25:
            lives -= 1
            fireballs.remove(fireball)
            if lives <= 0:
                game_over = True


# 일시 정지 화면 표시 함수
def show_pause_menu():
    screen.fill(BLACK)
    pause_text = font.render("Game Paused", True, WHITE)
    screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 100))

    # Continue 버튼
    continue_button = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2, 150, 40)
    pygame.draw.rect(screen, BLUE, continue_button)
    continue_text = font.render("Continue", True, WHITE)
    screen.blit(continue_text, (continue_button.x + 5, continue_button.y + 5))

    # Restart 버튼
    restart_button = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2 + 60, 150, 40)
    pygame.draw.rect(screen, NAVY, restart_button)
    restart_text = font.render("Restart", True, WHITE)
    screen.blit(restart_text, (restart_button.x + 15, restart_button.y + 5))

    # Menu 버튼
    menu_button = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2 + 120, 150, 40)
    pygame.draw.rect(screen, GREEN, menu_button)
    menu_text = font.render("Menu", True, WHITE)
    screen.blit(menu_text, (menu_button.x + 30, menu_button.y + 5))

    # Exit 버튼
    exit_button = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2 + 180, 150, 40)
    pygame.draw.rect(screen, RED, exit_button)
    exit_text = font.render("Exit", True, WHITE)
    screen.blit(exit_text, (exit_button.x + 35, exit_button.y + 5))

    pygame.display.flip()
    return continue_button, restart_button, menu_button, exit_button

# 메인 게임 루프
running = True
game_over = False
while running:
    if not game_started:
        # 초기 화면
        start_button, exit_button = show_start_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if start_button.collidepoint(mouse_pos):
                    game_started = True  # 게임 시작
                elif exit_button.collidepoint(mouse_pos):
                    running = False      # 게임 종료
        continue  # 초기 화면이 사라질 때까지 루프 지속

    # 메인 게임 화면
    screen.blit(background_image, (0, 0))
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # 일시 정지 상태 토글 (P키로 일시 정지)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            paused = not paused

        # 게임 종료 상태에서 리트라이 처리
        if game_over and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if retry_button.collidepoint(mouse_pos):
                score = 0
                level = 1
                lives = 3
                scroll_speed = 5
                blackholes = [create_blackhole() for _ in range(2)]
                obstacles = [create_obstacle() for _ in range(5)]
                dusts = [create_dust() for _ in range(10)]
                rocket_pos = [WIDTH // 2, HEIGHT // 2]
                obstacle_angles = [0] * len(obstacles)
                obstacle_speeds = [random.randint(1, 10) for _ in range(len(obstacles))]
                extra_lives.clear()
                fireballs.clear()
                game_over = False

    # 일시 정지 상태 처리
    if paused:
        continue_button, restart_button, menu_button, exit_button = show_pause_menu()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if continue_button.collidepoint(mouse_pos):
                    paused = False  # 게임 계속
                elif restart_button.collidepoint(mouse_pos):
                    reset_game()  # 게임 재시작
                    paused = False
                elif menu_button.collidepoint(mouse_pos):
                    reset_game()
                    game_started = False  # 초기 화면으로 돌아가기
                    paused = False
                elif exit_button.collidepoint(mouse_pos):
                    running = False  # 게임 종료
        continue  # 일시 정지 상태에서는 게임 루프 중단

    if not game_over:
        if score >= level * level_up_score_threshold:
            level += 1
            scroll_speed = min(scroll_speed + 1, max_scroll_speed)
            obstacles.append(create_obstacle())
            obstacle_angles.append(0)
            obstacle_speeds.append(random.randint(1, 10))
            if level % 2 == 0:
                blackholes.append(create_blackhole())
            extra_lives.append(create_extra_life())
        if level >= 4 and current_time - last_fireball_time > fireball_spawn_interval:
            create_fireballs()
            last_fireball_time = current_time

        handle_invincibility()
        keys = pygame.key.get_pressed()
        move_rocket(keys)
        check_collisions()
        check_blackhole_collision()
        move_fireballs()
        render_rocket()
        
        # 화면 그리기
        for fireball in fireballs:
            screen.blit(fireball_image, fireball["rect"].topleft)

        for dust in dusts:
            dust.y += scroll_speed
            if dust.y > HEIGHT:
                dusts.remove(dust)
                dusts.append(create_dust())
            screen.blit(dust_image, dust.topleft)

        for i, obstacle in enumerate(obstacles):
            obstacle.y += scroll_speed
            if obstacle.y > HEIGHT:
                obstacles.remove(obstacle)
                obstacles.append(create_obstacle())
                obstacle_angles.pop(i)
                obstacle_speeds.pop(i)
                obstacle_angles.append(0)
                obstacle_speeds.append(random.randint(1, 10))
            obstacle_angles[i] = (obstacle_angles[i] + obstacle_speeds[i]) % 360
            rotated_rock_image = pygame.transform.rotate(rock_image, obstacle_angles[i])
            rotated_rect = rotated_rock_image.get_rect(center=(obstacle.x + 20, obstacle.y + 20))
            screen.blit(rotated_rock_image, rotated_rect.topleft)

        for life in extra_lives[:]:
            if math.hypot(rocket_pos[0] - life.centerx, rocket_pos[1] - life.centery) < 25:
                lives = min(lives + 1, max_lives)
                extra_lives.remove(life)

        for life in extra_lives:
            life.y += scroll_speed
            if life.y > HEIGHT:
                extra_lives.remove(life)
            else:
                screen.blit(heart_image, life)

        for blackhole in blackholes:
            blackhole.y += scroll_speed - 1
            if blackhole.y > HEIGHT:
                blackholes.remove(blackhole)
                blackholes.append(create_blackhole())
            screen.blit(blackhole_image, blackhole)

        rotated_rocket_rect = rocket_image.get_rect(center=(rocket_pos[0], rocket_pos[1]))
        screen.blit(rocket_image, rotated_rocket_rect.topleft)

        score_text = font.render(f"Score: {score}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        highscore_text = font.render(f"Highscore: {highscore}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 50))
        screen.blit(highscore_text, (10, 90))
        for i in range(lives):
            screen.blit(heart_image, (WIDTH - (i + 1) * 40, 10))

    else:
        screen.fill(BLACK)
        end_text = font.render(f"Game Over! Final Score: {score}", True, WHITE)
        screen.blit(end_text, (WIDTH // 2 - end_text.get_width() // 2, HEIGHT // 2 - 100))
        if score > highscore:
            highscore = score
        highscore_text = font.render(f"Highscore: {highscore}", True, WHITE)
        screen.blit(highscore_text, (WIDTH // 2 - highscore_text.get_width() // 2, HEIGHT // 2 - 60))

        # Retry 버튼
        retry_button = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2, 100, 40)
        pygame.draw.rect(screen, NAVY, retry_button)
        retry_text = font.render("Retry", True, WHITE)
        screen.blit(retry_text, (retry_button.x + 10, retry_button.y + 5))

        # Menu 버튼
        menu_button = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 60, 100, 40)
        pygame.draw.rect(screen, GREEN, menu_button)
        menu_text = font.render("Menu", True, WHITE)
        screen.blit(menu_text, (menu_button.x + 15, menu_button.y + 5))

        # Exit 버튼
        exit_button = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 120, 100, 40)
        pygame.draw.rect(screen, RED, exit_button)
        exit_text = font.render("Exit", True, WHITE)
        screen.blit(exit_text, (exit_button.x + 20, exit_button.y + 5))

        pygame.display.flip()

        # 버튼 클릭 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if retry_button.collidepoint(mouse_pos):
                    reset_game()  # 게임 재시작
                    game_over = False
                elif menu_button.collidepoint(mouse_pos):
                    reset_game()
                    game_started = False  # 초기 화면으로 돌아가기
                    paused = False
                elif exit_button.collidepoint(mouse_pos):
                    running = False  # 게임 종료
        continue  # 게임 오버 상태에서는 루프 중단

    pygame.display.flip()
    clock.tick(40)

pygame.quit()
