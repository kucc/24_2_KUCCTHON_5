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
lives = 3  # 플레이어의 초기 목숨 수
max_lives = 5  # 최대 목숨 개수

# 레벨 시스템 추가
level = 1
level_up_score_threshold = 100  # 각 레벨에서 필요한 점수

# 로켓 설정
rocket_image = pygame.image.load("rocket.png")  # 로켓 이미지 로드
rocket_image = pygame.transform.scale(rocket_image, (50, 50))  # 로켓 크기를 50x50으로 조정
rocket_pos = [WIDTH // 2, HEIGHT // 2]  # 화면 중앙에서 시작
rocket_angle = 0  # 로켓의 회전 각도
original_rocket_image = rocket_image  # 원래의 로켓 이미지 보관

# 하트 이미지 로드 및 크기 설정
heart_image = pygame.image.load("heart.png")
heart_image = pygame.transform.scale(heart_image, (30, 30))  # 하트 이미지 크기를 30x30으로 조정

# 먼지 이미지 로드 및 크기 설정
dust_image = pygame.image.load("star.png")
dust_image = pygame.transform.scale(dust_image, (15, 15))  # 먼지 이미지를 15x15 크기로 조정

# 장애물 및 먼지 리스트
dusts = []
obstacles = []
blackholes = []
extra_lives = []  # 화면에 표시되는 목숨 아이템 목록

# 장애물 이미지 로드
rock_image = pygame.image.load("rock_obstacle.png")  # 기존 운석 이미지
rock_image = pygame.transform.scale(rock_image, (40, 40))  # 운석 크기를 40x40으로 조정

# 블랙홀 이미지 로드
blackhole_image = pygame.image.load("black.png")  # 블랙홀 이미지 (black.png 파일)
blackhole_image = pygame.transform.scale(blackhole_image, (80, 80))  # 블랙홀 크기를 80x80으로 조정

# 각 운석의 회전 각도와 회전 속도 리스트
obstacle_angles = [0] * 5  # 초기 운석 개수만큼 각도 0으로 설정
obstacle_speeds = [random.randint(1, 10) for _ in range(5)]  # 각 운석의 회전 속도를 1~10 범위에서 랜덤으로 설정

# 먼지 및 장애물 생성 함수
def create_dust():
    x = random.randint(0, WIDTH)
    y = random.randint(-HEIGHT, 0)
    return pygame.Rect(x, y, 15, 15)  # 먼지의 크기를 이미지 크기인 15x15로 조정

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
    return pygame.Rect(x, y, 30, 30)  # 크기는 heart.png와 맞게 30x30으로 설정

# 초기 먼지 및 장애물 생성
for _ in range(10):
    dusts.append(create_dust())
for _ in range(5):
    obstacles.append(create_obstacle())
for _ in range(2):  # 블랙홀은 적은 빈도로 나타나도록 설정
    blackholes.append(create_blackhole())

# 로켓 이동 함수
def move_rocket(keys):
    global rocket_image, rocket_angle

    # A와 D 키에 따라 로켓 기울기 조정
    if keys[pygame.K_a]:
        rocket_angle = 45  # 왼쪽으로 기울기
    elif keys[pygame.K_d]:
        rocket_angle = -45  # 오른쪽으로 기울기
    else:
        rocket_angle = 0  # 키에서 손을 떼면 원래 상태로 복구

    # 회전된 로켓 이미지 생성
    rocket_image = pygame.transform.rotate(original_rocket_image, rocket_angle)
    if keys[pygame.K_w]: rocket_pos[1] -= 5
    if keys[pygame.K_s]: rocket_pos[1] += 5
    if keys[pygame.K_a]: rocket_pos[0] -= 5
    if keys[pygame.K_d]: rocket_pos[0] += 5

# 픽셀 충돌 체크 함수
def check_pixel_collision(obstacle):
    rotated_rocket_rect = rocket_image.get_rect(center=(rocket_pos[0], rocket_pos[1]))
    obstacle_rect = rock_image.get_rect(center=(obstacle.x, obstacle.y))

    # 충돌 체크를 위한 mask 생성
    rocket_mask = pygame.mask.from_surface(rocket_image)
    obstacle_mask = pygame.mask.from_surface(rock_image)

    # 두 개의 rect 중심에서 offset 계산
    offset = (obstacle_rect.x - rotated_rocket_rect.x, obstacle_rect.y - rotated_rocket_rect.y)
    collision_point = rocket_mask.overlap(obstacle_mask, offset)

    return collision_point is not None  # 충돌 여부 반환

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
                # 게임 리셋
                score = 0
                level = 1
                lives = 3  # 목숨 초기화
                scroll_speed = 2
                blackholes = [create_blackhole() for _ in range(2)]
                obstacles = [create_obstacle() for _ in range(5)]
                dusts = [create_dust() for _ in range(10)]
                rocket_pos = [WIDTH // 2, HEIGHT // 2]
                obstacle_angles = [0] * len(obstacles)  # 각도 초기화
                obstacle_speeds = [random.randint(1, 10) for _ in range(len(obstacles))]  # 각 운석의 회전 속도 재설정
                extra_lives.clear()  # 목숨 아이템 초기화
                game_over = False

    if not game_over:
        # 점수에 따라 레벨 업
        if score >= level * level_up_score_threshold:
            level += 1
            scroll_speed = min(scroll_speed + 1, max_scroll_speed)  # 속도 증가
            obstacles.append(create_obstacle())  # 장애물 추가
            obstacle_angles.append(0)  # 새 장애물의 초기 각도 추가
            obstacle_speeds.append(random.randint(1, 10))  # 새 장애물의 회전 속도 추가
            if level % 2 == 0:
                blackholes.append(create_blackhole())  # 블랙홀 추가
            
            # 목숨 아이템 추가
            extra_lives.append(create_extra_life())

        keys = pygame.key.get_pressed()
        move_rocket(keys)
        check_collisions()
        check_blackhole_collision()

        for dust in dusts:
            dust.y += scroll_speed
            if dust.y > HEIGHT:
                dusts.remove(dust)
                dusts.append(create_dust())

        for i, obstacle in enumerate(obstacles):
            obstacle.y += scroll_speed
            if obstacle.y > HEIGHT:
                obstacles.remove(obstacle)
                obstacles.append(create_obstacle())
                obstacle_angles.pop(i)
                obstacle_speeds.pop(i)
                obstacle_angles.append(0)
                obstacle_speeds.append(random.randint(1, 10))  # 새로운 장애물의 회전 속도 추가

            # 운석 회전 각도를 각기 다른 속도로 증가시키고 회전된 이미지 생성
            obstacle_angles[i] = (obstacle_angles[i] + obstacle_speeds[i]) % 360  # 개별 속도만큼 회전
            rotated_rock_image = pygame.transform.rotate(rock_image, obstacle_angles[i])
            rotated_rect = rotated_rock_image.get_rect(center=(obstacle.x + 20, obstacle.y + 20))
            screen.blit(rotated_rock_image, rotated_rect.topleft)

        # 목숨 아이템 표시 및 충돌 처리
        for life in extra_lives[:]:
            if math.hypot(rocket_pos[0] - life.centerx, rocket_pos[1] - life.centery) < 25:
                lives = min(lives + 1, max_lives)  # 목숨 증가, 최대 5로 제한
                extra_lives.remove(life)  # 획득한 목숨 아이템 제거

        for life in extra_lives:
            life.y += scroll_speed
            if life.y > HEIGHT:
                extra_lives.remove(life)
            else:
                screen.blit(heart_image, life)

        for dust in dusts:
            screen.blit(dust_image, dust.topleft)

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
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 50))

        for i in range(lives):
            screen.blit(heart_image, (WIDTH - (i + 1) * 40, 10))  # 오른쪽 상단에 하트 이미지를 배치

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
