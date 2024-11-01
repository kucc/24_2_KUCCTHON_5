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
font = pygame.font.Font(None, 36)

# 게임 변수
clock = pygame.time.Clock()
score = 0
scroll_speed = 5
max_scroll_speed = 10
speed_increase_interval = 5000
lives = 3
max_lives = 5

# 레벨 시스템 추가
level = 1
level_up_score_threshold = 100

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
fireball_image = pygame.image.load("fire.png")  # 파이어볼 이미지 필요
fireball_image = pygame.transform.scale(fireball_image, (20, 20))

# 파이어볼 리스트
fireballs = []
fireball_spawn_interval = 7000
last_fireball_time = 0

# 각 운석의 회전 각도와 회전 속도 리스트
obstacle_angles = [0] * 5
obstacle_speeds = [random.randint(1, 10) for _ in range(5)]

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

# 파이어볼 생성 함수 (속도와 갯수를 레벨에 따라 설정)
def create_fireballs():
    fireball_count = 4 + (level - 4) // 3  # 4단계부터 4개, 이후 3단계마다 1개씩 증가
    fireballs.clear()  # 기존 파이어볼 제거 후 새로 생성
    for _ in range(fireball_count):
        x = random.randint(0, WIDTH)  # 항상 상단에서 생성
        y = 0
        direction_x = rocket_pos[0] - x
        direction_y = rocket_pos[1] - y
        distance = math.hypot(direction_x, direction_y)
        speed = 8  # 파이어볼 속도를 기존보다 빠르게 설정
        velocity_x = (direction_x / distance) * speed
        velocity_y = (direction_y / distance) * speed
        fireballs.append({"rect": pygame.Rect(x, y, 20, 20), "velocity": (velocity_x, velocity_y)})
# 픽셀 충돌 체크 함수 (장애물과 로켓의 픽셀 단위 충돌)
def check_pixel_collision(obstacle):
    rotated_rocket_rect = rocket_image.get_rect(center=(rocket_pos[0], rocket_pos[1]))
    obstacle_rect = rock_image.get_rect(center=(obstacle.x, obstacle.y))
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
        if check_pixel_collision(obstacle):  # 픽셀 충돌 검사
            lives -= 1  # 충돌 시 목숨 감소
            obstacles.remove(obstacle)  # 충돌한 장애물 제거
            obstacles.append(create_obstacle())  # 새로운 장애물 생성
            obstacle_angles.pop(i)  # 회전 각도 초기화
            obstacle_speeds.pop(i)  # 제거된 운석의 회전 속도도 삭제
            obstacle_angles.append(0)  # 새로운 장애물의 초기 각도 추가
            obstacle_speeds.append(random.randint(1, 10))  # 새로운 장애물의 회전 속도 추가
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
                game_over = True

# 초기 먼지 및 장애물 생성
for _ in range(10):
    dusts.append(create_dust())
for _ in range(5):
    obstacles.append(create_obstacle())
for _ in range(2):
    blackholes.append(create_blackhole())

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

# 메인 게임 루프
running = True
game_over = False
while running:
    screen.fill(BLACK)
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_over and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if retry_button.collidepoint(mouse_pos):
                score = 0
                level = 1
                lives = 3
                scroll_speed = 2
                blackholes = [create_blackhole() for _ in range(2)]
                obstacles = [create_obstacle() for _ in range(5)]
                dusts = [create_dust() for _ in range(10)]
                rocket_pos = [WIDTH // 2, HEIGHT // 2]
                obstacle_angles = [0] * len(obstacles)
                obstacle_speeds = [random.randint(1, 10) for _ in range(len(obstacles))]
                extra_lives.clear()
                fireballs.clear()
                game_over = False

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

        # 파이어볼 생성 조건 (4단계 이상일 때)
        if level >= 4 and current_time - last_fireball_time > fireball_spawn_interval:
            create_fireballs()
            last_fireball_time = current_time

        keys = pygame.key.get_pressed()
        move_rocket(keys)
        check_collisions()
        check_blackhole_collision()
        move_fireballs()

        for fireball in fireballs:
            screen.blit(fireball_image, fireball["rect"].topleft)

        # 먼지, 장애물, 블랙홀 등 화면 표시 및 업데이트 코드
        # (위에서 설명한 코드들을 여기에 추가)
        for dust in dusts:
            dust.y += scroll_speed
            if dust.y > HEIGHT:
                dusts.remove(dust)
                dusts.append(create_dust())
            screen.blit(dust_image, dust.topleft)

        # 장애물 이동 및 회전 처리 및 화면 표시
        for i, obstacle in enumerate(obstacles):
            obstacle.y += scroll_speed
            if obstacle.y > HEIGHT:
                obstacles.remove(obstacle)
                obstacles.append(create_obstacle())
                obstacle_angles.pop(i)
                obstacle_speeds.pop(i)
                obstacle_angles.append(0)
                obstacle_speeds.append(random.randint(1, 10))

            # 운석 회전 각도 증가 및 회전된 이미지 생성
            obstacle_angles[i] = (obstacle_angles[i] + obstacle_speeds[i]) % 360
            rotated_rock_image = pygame.transform.rotate(rock_image, obstacle_angles[i])
            rotated_rect = rotated_rock_image.get_rect(center=(obstacle.x + 20, obstacle.y + 20))
            screen.blit(rotated_rock_image, rotated_rect.topleft)

        # 추가 목숨 아이템 표시 및 충돌 처리
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

        # 블랙홀 이동 및 화면 표시
        for blackhole in blackholes:
            blackhole.y += scroll_speed - 1
            if blackhole.y > HEIGHT:
                blackholes.remove(blackhole)
                blackholes.append(create_blackhole())
            screen.blit(blackhole_image, blackhole)

        # 로켓 회전 및 위치 업데이트 후 화면 표시
        rotated_rocket_rect = rocket_image.get_rect(center=(rocket_pos[0], rocket_pos[1]))
        screen.blit(rocket_image, rotated_rocket_rect.topleft)

        # 점수 및 레벨 텍스트 표시
        score_text = font.render(f"Score: {score}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 50))

        # 목숨 이미지 표시
        for i in range(lives):
            screen.blit(heart_image, (WIDTH - (i + 1) * 40, 10))

    else:
        screen.fill(BLACK)
        end_text = font.render(f"Game Over! Final Score: {score}", True, WHITE)
        screen.blit(end_text, (WIDTH // 2 - end_text.get_width() // 2, HEIGHT // 2 - 30))
        retry_button = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 50, 100, 40)
        pygame.draw.rect(screen, BLUE, retry_button)
        retry_text = font.render("Retry", True, WHITE)
        screen.blit(retry_text, (retry_button.x + 10, retry_button.y + 5))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
