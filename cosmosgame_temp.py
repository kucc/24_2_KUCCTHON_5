import pygame
import random
import math

# 초기 설정
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("무한 우주 먼지 수집 로켓")

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# 폰트 설정
font = pygame.font.Font("game_font_1.ttf", 28)

# 게임 변수
clock = pygame.time.Clock()
score = 0
highscore = 0
base_scroll_speed = 5
scroll_speed = base_scroll_speed
max_scroll_speed = 20  # 난이도 증가에 맞춰 최대 스크롤 속도 조정
base_speed = 5  # 고정된 로켓 속도
lives = 3
max_lives = 5

# 레벨 시스템 추가
level = 1
level_up_score_threshold = 100

# 보스 레이드 트리거를 위한 변수
last_boss_raid_score = 0  # 마지막 보스 레이드가 시작된 점수

# 배경 이미지 로드 및 크기 설정
background_image = pygame.image.load("background1.png")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

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

# 보스 레이드 상태 변수
BOSS_RAID = False
boss_image_original = pygame.image.load("boss.png")
boss_image_original = pygame.transform.scale(boss_image_original, (150, 150))  # 초기 크기 증가
boss_image = boss_image_original
boss_rect = boss_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
boss_velocity = [0, 0]  # 초기에는 정지 상태
boss_growing = True
boss_scale_increment = 0.02  # 보스 크기 증가 속도 조정
boss_current_scale = 1.0
boss_spawn_time = 0
boss_duration = 6  # 기본 생존 시간 (초)
boss_survival_time = boss_duration

# 초기 화면 표시 함수
def show_start_screen():
    screen.fill(BLACK)
    title_text = font.render("무한 우주 먼지 수집 로켓", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 100))
    
    # Start 버튼
    start_button = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2, 100, 40)
    pygame.draw.rect(screen, BLUE, start_button)
    start_text = font.render("Start", True, WHITE)
    screen.blit(start_text, (start_button.x + 10, start_button.y + 5))

    # Exit 버튼
    exit_button = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 60, 100, 40)
    pygame.draw.rect(screen, BLUE, exit_button)
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
        if distance == 0:
            distance = 1  # 제로 디비전 방지
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
    obstacle_rect = rock_image.get_rect(center=(obstacle.x + obstacle.width//2, obstacle.y + obstacle.height//2))
    rocket_mask = pygame.mask.from_surface(rocket_image)
    obstacle_mask = pygame.mask.from_surface(rock_image)
    offset = (obstacle_rect.x - rotated_rocket_rect.x, obstacle_rect.y - rotated_rocket_rect.y)
    collision_point = rocket_mask.overlap(obstacle_mask, offset)
    return collision_point is not None

# 충돌 체크 함수
def check_collisions():
    global score, lives, game_over
    for dust in dusts[:]:
        if math.hypot(rocket_pos[0] - dust.x, rocket_pos[1] - dust.y) < 25:
            score += 10
            dusts.remove(dust)
            dusts.append(create_dust())

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
                lives -= 1  # 블랙홀과의 충돌 시 생명 1칸 소모
                if lives <= 0:
                    game_over = True

# 보스의 속도를 로켓을 향해 조정하는 함수
def update_boss_velocity():
    global boss_velocity
    dx = rocket_pos[0] - boss_rect.centerx
    dy = rocket_pos[1] - boss_rect.centery
    distance = math.hypot(dx, dy)
    if distance != 0:
        dx /= distance
        dy /= distance
    boss_speed = 3  # 보스의 이동 속도 조정 가능
    boss_velocity = [dx * boss_speed, dy * boss_speed]

# 보스 스폰 위치 조정 함수 (로켓으로부터 일정 거리 이상 떨어진 위치에 스폰)
def get_boss_spawn_position():
    min_distance = 200  # 최소 스폰 거리 설정
    while True:
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        distance = math.hypot(rocket_pos[0] - x, rocket_pos[1] - y)
        if distance >= min_distance:
            return x, y

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
    global highscore, boss_survival_time, last_boss_raid_score
    score = 0
    level = 1
    lives = 3
    scroll_speed = base_scroll_speed
    blackholes = [create_blackhole() for _ in range(2)]
    obstacles = [create_obstacle() for _ in range(5)]
    dusts = [create_dust() for _ in range(10)]
    rocket_pos = [WIDTH // 2, HEIGHT // 2]
    obstacle_angles = [0] * len(obstacles)
    obstacle_speeds = [random.randint(1, 10) for _ in range(len(obstacles))]
    extra_lives.clear()
    fireballs.clear()
    game_over = False
    boss_survival_time = boss_duration
    last_boss_raid_score = 0  # 초기화

# 로켓 이동 함수
def move_rocket(keys):
    global rocket_image, rocket_angle
    if keys[pygame.K_a]:
        rocket_angle = 45
    elif keys[pygame.K_d]:
        rocket_angle = -45
    else:
        rocket_angle = 0
    rocket_image = pygame.transform.rotate(original_rocket_image, rocket_angle)
    if keys[pygame.K_w]:
        rocket_pos[1] -= base_speed
    if keys[pygame.K_s]:
        rocket_pos[1] += base_speed
    if keys[pygame.K_a]:
        rocket_pos[0] -= base_speed
    if keys[pygame.K_d]:
        rocket_pos[0] += base_speed
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
    pygame.draw.rect(screen, BLUE, restart_button)
    restart_text = font.render("Restart", True, WHITE)
    screen.blit(restart_text, (restart_button.x + 15, restart_button.y + 5))

    # Menu 버튼
    menu_button = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2 + 120, 150, 40)
    pygame.draw.rect(screen, BLUE, menu_button)
    menu_text = font.render("Menu", True, WHITE)
    screen.blit(menu_text, (menu_button.x + 30, menu_button.y + 5))

    # Exit 버튼
    exit_button = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2 + 180, 150, 40)
    pygame.draw.rect(screen, BLUE, exit_button)
    exit_text = font.render("Exit", True, WHITE)
    screen.blit(exit_text, (exit_button.x + 35, exit_button.y + 5))

    pygame.display.flip()
    return continue_button, restart_button, menu_button, exit_button

# 보스 레이드 화면 표시 함수
def show_boss_raid():
    screen.blit(background_image, (0, 0))
    
    # 보스 이미지 그리기
    screen.blit(boss_image, boss_rect.topleft)
    
    # 남은 생명 표시
    for i in range(lives):
        screen.blit(heart_image, (WIDTH - (i + 1) * 40, 10))
    
    # 보스 생존 타이머 표시
    elapsed_time = (pygame.time.get_ticks() - boss_spawn_time) / 1000
    remaining_time = boss_survival_time - elapsed_time
    if remaining_time < 0:
        remaining_time = 0
    timer_text = font.render(f"Survive for {int(remaining_time)} seconds!", True, WHITE)
    screen.blit(timer_text, (WIDTH // 2 - timer_text.get_width() // 2, 20))
    
    pygame.display.flip()

# 메인 게임 루프
running = True
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
    if not BOSS_RAID:
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
                reset_game()  # 게임 재시작
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

    if BOSS_RAID and not game_over:
        # 보스 레이드 상태
        show_boss_raid()
        
        # 로켓 이동 처리 (보스 레이드 중에도 조작 가능)
        keys = pygame.key.get_pressed()
        move_rocket(keys)

        # 보스의 속도를 로켓을 향해 업데이트
        update_boss_velocity()

        # 보스 움직임 업데이트
        boss_rect.x += boss_velocity[0]
        boss_rect.y += boss_velocity[1]

        # 보스가 화면 밖으로 나가지 않도록 위치 조정
        boss_rect.x = max(0, min(WIDTH - boss_rect.width, boss_rect.x))
        boss_rect.y = max(0, min(HEIGHT - boss_rect.height, boss_rect.y))

        # 보스 크기 증가/감소
        if boss_growing:
            boss_current_scale += boss_scale_increment
            new_size = (int(150 * boss_current_scale), int(150 * boss_current_scale))  # 보스 크기 증가
            boss_image = pygame.transform.scale(boss_image_original, new_size)
            boss_rect = boss_image.get_rect(center=boss_rect.center)
            if boss_current_scale >= 3.0:  # 최대 크기 설정
                boss_growing = False
        else:
            if boss_current_scale > 1.0:
                boss_current_scale -= boss_scale_increment
                new_size = (int(150 * boss_current_scale), int(150 * boss_current_scale))
                boss_image = pygame.transform.scale(boss_image_original, new_size)
                boss_rect = boss_image.get_rect(center=boss_rect.center)

        # 보스 생존 타이머 업데이트
        elapsed_time = (pygame.time.get_ticks() - boss_spawn_time) / 1000
        remaining_time = boss_survival_time - elapsed_time
        if remaining_time <= 0:
            BOSS_RAID = False  # 보스 레이드 종료
            # 추가적인 레벨 업 로직이나 보상 로직을 여기에 추가할 수 있습니다.
        else:
            # 충돌 체크: 로켓과 보스 간 충돌
            if math.hypot(rocket_pos[0] - boss_rect.centerx, rocket_pos[1] - boss_rect.centery) < (boss_rect.width // 2):
                lives -= 2  # 보스와 충돌 시 생명 2칸 소모
                if lives <= 0:
                    game_over = True
                else:
                    # 보스 레이드 지속을 위해 보스의 위치 재조정
                    new_x, new_y = get_boss_spawn_position()
                    boss_rect.center = (new_x, new_y)
                    boss_growing = True
                    boss_current_scale = 1.0

        # 화면 그리기 (로켓, 보스)
        screen.blit(boss_image, boss_rect.topleft)

        rotated_rocket_rect = rocket_image.get_rect(center=(rocket_pos[0], rocket_pos[1]))
        screen.blit(rocket_image, rotated_rocket_rect.topleft)

        # 남은 시간 UI는 show_boss_raid 함수에서 이미 처리됨

    elif not game_over:
        # 레벨 업 체크 및 보스 레이드 트리거
        if (level >=4 and last_boss_raid_score ==0) or (level >=4 and score >= last_boss_raid_score + 300):
            BOSS_RAID = True
            boss_spawn_time = pygame.time.get_ticks()
            boss_current_scale = 1.0
            boss_growing = True
            # 보스 스폰 위치 로켓으로부터 최소 거리 이상 떨어진 위치로 설정
            spawn_x, spawn_y = get_boss_spawn_position()
            boss_rect.center = (spawn_x, spawn_y)
            boss_image = pygame.transform.scale(boss_image_original, (150, 150))  # 보스 초기 크기 유지
            # 보스의 초기 속도는 0으로 설정한 후, 추적 로직에서 업데이트됨
            boss_velocity = [0, 0]
            # 보스 생존 시간 증가
            boss_survival_time += 1
            # 마지막 보스 레이드 점수 업데이트
            last_boss_raid_score = score

        if score >= last_boss_raid_score + 300 and level >=4:
            BOSS_RAID = True
            boss_spawn_time = pygame.time.get_ticks()
            boss_current_scale = 1.0
            boss_growing = True
            # 보스 스폰 위치 로켓으로부터 최소 거리 이상 떨어진 위치로 설정
            spawn_x, spawn_y = get_boss_spawn_position()
            boss_rect.center = (spawn_x, spawn_y)
            boss_image = pygame.transform.scale(boss_image_original, (150, 150))  # 보스 초기 크기 유지
            boss_velocity = [0, 0]
            # 보스 생존 시간 증가
            boss_survival_time += 1
            # 마지막 보스 레이드 점수 업데이트
            last_boss_raid_score = score

        if level % 4 !=0 and ((level >=4 and score >= last_boss_raid_score + 300)):
            # 보스 레이드 트리거 조건 재확인
            BOSS_RAID = True
            boss_spawn_time = pygame.time.get_ticks()
            boss_current_scale = 1.0
            boss_growing = True
            # 보스 스폰 위치 로켓으로부터 최소 거리 이상 떨어진 위치로 설정
            spawn_x, spawn_y = get_boss_spawn_position()
            boss_rect.center = (spawn_x, spawn_y)
            boss_image = pygame.transform.scale(boss_image_original, (150, 150))  # 보스 초기 크기 유지
            boss_velocity = [0, 0]
            # 보스 생존 시간 증가
            boss_survival_time += 1
            # 마지막 보스 레이드 점수 업데이트
            last_boss_raid_score = score

        if score >= level * level_up_score_threshold:
            level += 1
            scroll_speed = min(base_scroll_speed + (level - 1) * 1.0, max_scroll_speed)  # 레벨에 따라 스크롤 속도 증가 폭 확대
            obstacles.append(create_obstacle())
            obstacle_angles.append(0)
            obstacle_speeds.append(random.randint(1, 10))
            if level % 2 == 0:
                blackholes.append(create_blackhole())
            extra_lives.append(create_extra_life())

        if level >= 4 and current_time - last_fireball_time > fireball_spawn_interval:
            create_fireballs()
            last_fireball_time = current_time

        keys = pygame.key.get_pressed()
        move_rocket(keys)
        check_collisions()
        check_blackhole_collision()
        move_fireballs()
        
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
        # 게임 오버 화면
        screen.fill(BLACK)
        end_text = font.render(f"Game Over! Final Score: {score}", True, WHITE)
        screen.blit(end_text, (WIDTH // 2 - end_text.get_width() // 2, HEIGHT // 2 - 100))
        if score > highscore:
            highscore = score
        highscore_text = font.render(f"Highscore: {highscore}", True, WHITE)
        screen.blit(highscore_text, (WIDTH // 2 - highscore_text.get_width() // 2, HEIGHT // 2 - 60))

        # Retry 버튼
        retry_button = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2, 100, 40)
        pygame.draw.rect(screen, BLUE, retry_button)
        retry_text = font.render("Retry", True, WHITE)
        screen.blit(retry_text, (retry_button.x + 10, retry_button.y + 5))

        # Menu 버튼
        menu_button = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 60, 100, 40)
        pygame.draw.rect(screen, BLUE, menu_button)
        menu_text = font.render("Menu", True, WHITE)
        screen.blit(menu_text, (menu_button.x + 15, menu_button.y + 5))

        # Exit 버튼
        exit_button = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 120, 100, 40)
        pygame.draw.rect(screen, BLUE, exit_button)
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
                    game_over = False
                elif exit_button.collidepoint(mouse_pos):
                    running = False  # 게임 종료
        continue  # 게임 오버 상태에서는 루프 중단

    # 보스 레이드 종료 후 게임 상태 초기화
    if BOSS_RAID and not game_over:
        elapsed_time = (pygame.time.get_ticks() - boss_spawn_time) / 1000
        if elapsed_time >= boss_survival_time:
            BOSS_RAID = False
            # 추가적인 레벨 업 로직이나 보상 로직을 여기에 추가할 수 있습니다.

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
