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
NAVY = (75, 0, 130)
PURPLE = (143, 0, 255)
GRAY = (128, 128, 128)  # *** Added: GRAY 색상 추가 ***

# 폰트 설정
font = pygame.font.Font("game_font_1.ttf", 28)

# 아이콘 설정
icon_image = pygame.image.load("icon.png")  # 아이콘 이미지 파일 로드
pygame.display.set_icon(icon_image)  # 프로그램 아이콘 설정

# 게임 변수
clock = pygame.time.Clock()
score = 0
highscore = 0
base_scroll_speed = 5
scroll_speed = base_scroll_speed
max_scroll_speed = 20
base_speed = 5
lives = 3
max_lives = 5

# 레벨 시스템 및 보스 레이드 변수
level = 1
level_up_score_threshold = 100
last_boss_raid_score = 0  # Tracks the score at the last boss raid completion

# 배경 이미지 로드 및 크기 설정
background_image = pygame.image.load("background1.png")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# 배경 이미지2 로드
background_image_2 = pygame.image.load("background2.png")
background_image_2 = pygame.transform.scale(background_image_2, (WIDTH, HEIGHT))

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

# 보스 레이드 상태 변수
BOSS_RAID = False
boss_image_original = pygame.image.load("boss.png")
boss_image_original = pygame.transform.scale(boss_image_original, (150, 150))
boss_image = boss_image_original
boss_rect = boss_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
boss_velocity = [0, 0]
boss_growing = True
boss_scale_increment = 0.02
boss_current_scale = 1.0
boss_spawn_time = 0
boss_duration = 6
boss_survival_time = boss_duration

# 보스 속도 업데이트 함수
def update_boss_velocity():
    global boss_velocity
    dx = rocket_pos[0] - boss_rect.centerx
    dy = rocket_pos[1] - boss_rect.centery
    distance = math.hypot(dx, dy)
    if distance != 0:
        dx /= distance
        dy /= distance
    boss_speed = 3
    boss_velocity = [dx * boss_speed, dy * boss_speed]

# 보스 스폰 위치 조정 함수
def get_boss_spawn_position():
    min_distance = 200  # Minimum distance from the rocket
    attempts = 0
    max_attempts = 100
    while attempts < max_attempts:
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)  # Spawn within the screen
        distance = math.hypot(rocket_pos[0] - x, rocket_pos[1] - y)
        if distance >= min_distance:
            return x, y
        attempts += 1
    # Fallback position if suitable position not found
    return random.randint(0, WIDTH), random.randint(0, HEIGHT)

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

# 게임 상태 변수 추가
game_state = "START"  # Possible states: START, MAIN_GAME, BOSS_RAID, PAUSED, GAME_OVER

# *** Added: 파티클 시스템 ***
class Particle:
    def __init__(self, pos, vel, radius, color, lifetime):
        self.pos = list(pos)
        self.vel = list(vel)
        self.radius = radius
        self.color = color
        self.lifetime = lifetime  # in milliseconds
        self.creation_time = pygame.time.get_ticks()

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        # Fade out over time
        elapsed = pygame.time.get_ticks() - self.creation_time
        if elapsed > self.lifetime:
            return False
        return True

    def draw(self, surface):
        elapsed = pygame.time.get_ticks() - self.creation_time
        alpha = max(255 - (255 * elapsed) // self.lifetime, 0)
        # Create a temporary surface for the particle with per-pixel alpha
        temp_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surface, self.color + (alpha,), (self.radius, self.radius), self.radius)
        surface.blit(temp_surface, (self.pos[0] - self.radius, self.pos[1] - self.radius))

particles = []  # List to hold all particles

def create_particle(pos, vel, radius, color, lifetime):
    particles.append(Particle(pos, vel, radius, color, lifetime))
# *** End of Added: 파티클 시스템 ***

# *** Added: 보스 레이드 후 부스터 및 무적 지속 변수 ***
post_boss_boost = False    # 보스 레이드 후 부스터 활성화 여부
boost_start_time = 0       # 부스터 시작 시간
BOOST_DURATION = 3000      # 부스터 지속 시간 (3초)
BOOST_MULTIPLIER = 2.5     # 부스터 속도 배율

# 초기 화면 표시 함수
def show_start_screen():
    screen.blit(background_image_2, (0, 0))  # Ensure background is drawn first
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
    global fireballs
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
        
        if distance == 0:
            distance = 1  # Prevent division by zero

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
        if pygame.time.get_ticks() - invincible_start_time > INVINCIBLE_DURATION and not post_boss_boost:
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
            # *** Added: 먼지를 먹을 때 파티클 생성 ***
            create_particle(dust.center, (0, -2), 5, YELLOW, 500)

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
                else:
                    # *** Added: 충돌 시 파티클 생성 ***
                    create_particle(rocket_pos, (random.uniform(-2, 2), random.uniform(-2, 2)), 7, RED, 700)
                    # 무적 상태 시작
                    invincible = True
                    invincible_start_time = pygame.time.get_ticks()
                return False
    return True

# 블랙홀 흡입 함수
def check_blackhole_collision():
    global rocket_pos, rocket_angle, game_over, lives
    # "BOSS_RAID" 상태일 때는 블랙홀과의 충돌을 무시
    if game_state == "BOSS_RAID":
        return
    for blackhole in blackholes:
        distance = math.hypot(rocket_pos[0] - blackhole.centerx, rocket_pos[1] - blackhole.centery)
        if distance < 100:
            direction_x = blackhole.centerx - rocket_pos[0]
            direction_y = blackhole.centery - rocket_pos[1]
            angle = math.atan2(direction_y, direction_x)
            rocket_pos[0] += math.cos(angle) * 3
            rocket_pos[1] += math.sin(angle) * 3
            rocket_angle += 10
            if distance < 10 and not post_boss_boost:
                game_over = True
            # *** Added: 블랙홀 근처에서 파티클 생성 ***
            create_particle(blackhole.center, (random.uniform(-1, 1), random.uniform(-1, 1)), 3, PURPLE, 300)

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
    global highscore, BOSS_RAID, last_boss_raid_score, game_state
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
    BOSS_RAID = False  # Reset boss raid status
    last_boss_raid_score = 0  # Reset last boss raid score
    game_state = "MAIN_GAME"  # Set game state to main game
    particles.clear()  # *** Added: 파티클 초기화 ***

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
        rocket_pos[1] -= 5
        # *** Modified: 회색 파티클 제거하고 하얀색 및 노란색 파티클 생성 ***
        create_particle((rocket_pos[0], rocket_pos[1] + 25), (random.uniform(-1, 1), 2), 3, WHITE, 500)
        create_particle((rocket_pos[0], rocket_pos[1] + 25), (random.uniform(-1, 1), 2), 3, YELLOW, 500)
    if keys[pygame.K_s]:
        rocket_pos[1] += 5
        # *** Modified: 회색 파티클 제거하고 하얀색 및 노란색 파티클 생성 ***
        create_particle((rocket_pos[0], rocket_pos[1] - 25), (random.uniform(-1, 1), -2), 3, WHITE, 500)
        create_particle((rocket_pos[0], rocket_pos[1] - 25), (random.uniform(-1, 1), -2), 3, YELLOW, 500)
    if keys[pygame.K_a]:
        rocket_pos[0] -= 5
        # *** Modified: 회색 파티클 제거하고 하얀색 및 노란색 파티클 생성 ***
        create_particle((rocket_pos[0] + 25, rocket_pos[1]), (2, random.uniform(-1, 1)), 3, WHITE, 500)
        create_particle((rocket_pos[0] + 25, rocket_pos[1]), (2, random.uniform(-1, 1)), 3, YELLOW, 500)
    if keys[pygame.K_d]:
        rocket_pos[0] += 5
        # *** Modified: 회색 파티클 제거하고 하얀색 및 노란색 파티클 생성 ***
        create_particle((rocket_pos[0] - 25, rocket_pos[1]), (-2, random.uniform(-1, 1)), 3, WHITE, 500)
        create_particle((rocket_pos[0] - 25, rocket_pos[1]), (-2, random.uniform(-1, 1)), 3, YELLOW, 500)
    rocket_pos[0] = max(0, min(WIDTH, rocket_pos[0]))
    rocket_pos[1] = max(0, min(HEIGHT, rocket_pos[1]))

# 파이어볼 이동 및 반사 처리 함수
def move_fireballs():
    global lives, game_over, invincible, invincible_start_time
    for fireball in fireballs[:]:
        fireball["rect"].x += fireball["velocity"][0]
        fireball["rect"].y += fireball["velocity"][1]
        
        # 화면 밖으로 나가는 파이어볼을 삭제
        if fireball["rect"].x <= 0 or fireball["rect"].x >= WIDTH - fireball["rect"].width:
            fireball["velocity"] = (-fireball["velocity"][0], fireball["velocity"][1])
        if fireball["rect"].y >= HEIGHT:
            fireballs.remove(fireball)
            continue
        
        # 파이어볼과 로켓의 충돌 검사
        if math.hypot(rocket_pos[0] - fireball["rect"].centerx, rocket_pos[1] - fireball["rect"].centery) < 25:
            if not invincible:  # 무적 상태가 아닐 때만 충돌 처리
                lives -= 1
                invincible = True  # 무적 상태 시작
                invincible_start_time = pygame.time.get_ticks()  # 무적 상태 시작 시간 설정
                # *** Added: 파이어볼과 충돌 시 파티클 생성 ***
                create_particle(fireball["rect"].center, (random.uniform(-2, 2), random.uniform(-2, 2)), 5, ORANGE, 700)
            fireballs.remove(fireball)
            if lives <= 0:
                game_over = True

# 일시 정지 화면 표시 함수
def show_pause_menu():
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

# 보스 레이드 화면 표시 함수
def show_boss_raid_screen():
    # Clear screen and show boss raid specific background or elements
    screen.blit(background_image, (0, 0))  # You can change this to a different background if desired
    boss_text = font.render("Boss Raid!", True, RED)
    screen.blit(boss_text, (WIDTH // 2 - boss_text.get_width() // 2, HEIGHT // 2 - 150))
    pygame.display.flip()

# 메인 게임 루프
running = True
while running:
    if game_state == "START":
        # 초기 화면
        start_button, exit_button = show_start_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if start_button.collidepoint(mouse_pos):
                    game_state = "MAIN_GAME"  # 게임 시작
                elif exit_button.collidepoint(mouse_pos):
                    running = False      # 게임 종료
        clock.tick(40)
        continue  # 초기 화면이 사라질 때까지 루프 지속

    elif game_state == "MAIN_GAME":
        # 메인 게임 화면
        screen.blit(background_image, (0, 0))
        current_time = pygame.time.get_ticks()

        if BOSS_RAID and not game_over:
            game_state = "BOSS_RAID"
            boss_spawn_time = pygame.time.get_ticks()
            boss_current_scale = 1.0
            boss_growing = True
            spawn_x, spawn_y = get_boss_spawn_position()
            boss_rect.center = (spawn_x, spawn_y)
            boss_image = pygame.transform.scale(boss_image_original, (150, 150))
            boss_velocity = [0, 0]
            boss_survival_time = boss_duration  # Reset survival time
            continue  # Move to next iteration to handle BOSS_RAID state

        # 레벨 업 체크 및 보스 레이드 트리거
        if level >= 4 and score >= last_boss_raid_score + 300:
            BOSS_RAID = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # 일시 정지 상태 토글 (P키로 일시 정지)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                game_state = "PAUSED"

            # 게임 종료 상태에서 리트라이 처리
            if game_over and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                # 게임 오버 상태에서는 'Retry', 'Menu', 'Exit' 버튼이 표시되므로 handle here
                # We'll handle game over in the "GAME_OVER" state
                pass

        # *** 부스터 활성화 상태일 때 스크롤 속도를 조절하고, 무적 상태 표시 ***
        if post_boss_boost:
            current_scroll_speed = scroll_speed * BOOST_MULTIPLIER
            if pygame.time.get_ticks() - boost_start_time >= BOOST_DURATION:
                post_boss_boost = False
                current_scroll_speed = scroll_speed
                invincible = False
            else:
                boost_text = font.render("BOOST MODE!", True, ORANGE)
                screen.blit(boost_text, (WIDTH // 2 - boost_text.get_width() // 2, HEIGHT // 2 - 80))
                invincible = True  # 부스터 동안 무적 상태 유지
        else:
            current_scroll_speed = scroll_speed  # 기본 스크롤 속도 적용

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
            
            # *** Added: 파티클 업데이트 및 그리기 ***
            for particle in particles[:]:
                if not particle.update():
                    particles.remove(particle)
                else:
                    particle.draw(screen)
            # *** End of Added: 파티클 업데이트 및 그리기 ***

            # 화면 그리기
            for fireball in fireballs:
                screen.blit(fireball_image, fireball["rect"].topleft)

            for dust in dusts:
                dust.y += current_scroll_speed
                if dust.y > HEIGHT:
                    dusts.remove(dust)
                    dusts.append(create_dust())
                screen.blit(dust_image, dust.topleft)

            for i, obstacle in enumerate(obstacles):
                obstacle.y += current_scroll_speed
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
                    # *** Added: 생명 획득 시 파티클 생성 ***
                    create_particle(life.center, (random.uniform(-1, 1), random.uniform(-1, 1)), 5, GREEN, 500)

            for life in extra_lives:
                life.y += current_scroll_speed
                if life.y > HEIGHT:
                    extra_lives.remove(life)
                else:
                    screen.blit(heart_image, life)

            for blackhole in blackholes:
                blackhole.y += current_scroll_speed - 1
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
            game_state = "GAME_OVER"

        pygame.display.flip()
        clock.tick(40)

    elif game_state == "BOSS_RAID":
        # 보스 레이드 상태
        screen.blit(background_image, (0, 0))  # Background for boss raid

        # 보스 움직임 업데이트
        update_boss_velocity()
        boss_rect.x += boss_velocity[0]
        boss_rect.y += boss_velocity[1]

        # 보스 크기 증가/감소
        if boss_growing:
            boss_current_scale += boss_scale_increment
            new_size = (int(150 * boss_current_scale), int(150 * boss_current_scale))
            boss_image = pygame.transform.scale(boss_image_original, new_size)
            boss_rect = boss_image.get_rect(center=(boss_rect.centerx, boss_rect.centery))
            if boss_current_scale >= 3.0:
                boss_growing = False
        else:
            if boss_current_scale > 1.0:
                boss_current_scale -= boss_scale_increment
                new_size = (int(150 * boss_current_scale), int(150 * boss_current_scale))
                boss_image = pygame.transform.scale(boss_image_original, new_size)
                boss_rect = boss_image.get_rect(center=(boss_rect.centerx, boss_rect.centery))

        # 보스 생존 타이머 업데이트
        elapsed_time = (pygame.time.get_ticks() - boss_spawn_time) / 1000
        remaining_time = boss_survival_time - elapsed_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # 일시 정지 상태 토글 (P키로 일시 정지)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                game_state = "PAUSED"

        if not game_over:
            # 레벨 업 체크 및 보스 레이드 종료
            if remaining_time <= 0:
                BOSS_RAID = False
                game_state = "MAIN_GAME"
                last_boss_raid_score = score  # **Update the last_boss_raid_score here**

                # *** 보스 레이드 후 부스터 상태 활성화 ***
                post_boss_boost = True
                boost_start_time = pygame.time.get_ticks()
                invincible = True

                continue  # Proceed to the main game

            # 로켓 이동 처리
            keys = pygame.key.get_pressed()
            move_rocket(keys)

            # 보스와 로켓 간 충돌 체크
            distance = math.hypot(rocket_pos[0] - boss_rect.centerx, rocket_pos[1] - boss_rect.centery)
            if distance < (boss_rect.width // 2):
                lives -= 2
                if lives <= 0:
                    game_over = True
                else:
                    new_x, new_y = get_boss_spawn_position()
                    boss_rect.center = (new_x, new_y)
                    boss_growing = True
                    boss_current_scale = 1.0
                    invincible = True
                    invincible_start_time = pygame.time.get_ticks()
                    # *** Added: 보스와 충돌 시 파티클 생성 ***
                    create_particle(rocket_pos, (random.uniform(-3, 3), random.uniform(-3, 3)), 10, RED, 1000)

            # 블랙홀 흡입 기능 유지 (optional)
            check_blackhole_collision()

            # *** Added: 파티클 업데이트 및 그리기 ***
            for particle in particles[:]:
                if not particle.update():
                    particles.remove(particle)
                else:
                    particle.draw(screen)
            # *** End of Added: 파티클 업데이트 및 그리기 ***

            handle_invincibility()
            check_blackhole_collision()

            # 화면 그리기
            rotated_rocket_rect = rocket_image.get_rect(center=(rocket_pos[0], rocket_pos[1]))
            screen.blit(rocket_image, rotated_rocket_rect.topleft)

            # 보스 이미지 그리기
            screen.blit(boss_image, boss_rect.topleft)

            # 보스 생존 타이머 표시
            timer_text = font.render(f"Survive for {int(remaining_time)} seconds!", True, WHITE)
            screen.blit(timer_text, (WIDTH // 2 - timer_text.get_width() // 2, 20))

            # 점수, 레벨, 하이스코어 및 생명 표시
            score_text = font.render(f"Score: {score}", True, WHITE)
            level_text = font.render(f"Level: {level}", True, WHITE)
            highscore_text = font.render(f"Highscore: {highscore}", True, WHITE)
            screen.blit(score_text, (10, 10))
            screen.blit(level_text, (10, 50))
            screen.blit(highscore_text, (10, 90))
            for i in range(lives):
                screen.blit(heart_image, (WIDTH - (i + 1) * 40, 10))

        else:
            game_state = "GAME_OVER"

        pygame.display.flip()
        clock.tick(40)

    elif game_state == "PAUSED":
        # 일시 정지 상태
        continue_button, restart_button, menu_button, exit_button = show_pause_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                # Continue 버튼
                if continue_button.collidepoint(mouse_pos):
                    game_state = "MAIN_GAME" if not BOSS_RAID else "BOSS_RAID"
                # Restart 버튼
                elif restart_button.collidepoint(mouse_pos):
                    reset_game()  # 게임 재시작
                # Menu 버튼
                elif menu_button.collidepoint(mouse_pos):
                    reset_game()
                    game_state = "START"  # 초기 화면으로 돌아가기
                # Exit 버튼
                elif exit_button.collidepoint(mouse_pos):
                    running = False  # 게임 종료
        clock.tick(40)
        continue  # 일시 정지 상태에서는 게임 루프 중단

    elif game_state == "GAME_OVER":
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
                    game_state = "MAIN_GAME"
                elif menu_button.collidepoint(mouse_pos):
                    reset_game()
                    game_state = "START"  # 초기 화면으로 돌아가기
                elif exit_button.collidepoint(mouse_pos):
                    running = False  # 게임 종료
        clock.tick(40)
        continue  # 게임 오버 상태에서는 루프 중단

pygame.quit()
