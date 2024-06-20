import pygame
import random
import os

class Stage:
    def __init__(self, width, height, foodlist):
        print("Initializing stage...")
        self.width = width  # 스테이지의 너비 (그리드의 열 수)
        self.height = height  # 스테이지의 높이 (그리드의 행 수)
        # 스테이지를 중앙에 배치하기 위한 x 좌표 계산
        self.x = (800 - ((width * 60) + ((width - 1) * 5))) // 2
        # 스테이지를 중앙에 배치하기 위한 y 좌표 계산
        self.y = (800 - ((height * 60) + ((height - 1) * 5))) // 2 - 45
        self.foodlist = foodlist  # 사용 가능한 그리드 타입 목록
        self.stage = []  # 그리드들을 저장할 리스트

        # 스테이지 초기화
        for j in range(height):
            tmp = []  # 임시 리스트
            for i in range(width):
                # Grid 객체를 생성하여 tmp 리스트에 추가
                tmp.append(Grid(self.x + i * 65, self.y + j * 65, j, i, random.choice(self.foodlist)))
            # 각 행의 그리드를 stage 리스트에 추가
            self.stage.append(tmp)
        print("Stage initialized.")

    def swap(self, pos1, pos2):
        # 두 그리드의 위치를 교환
        grid1 = self.stage[pos1[1]][pos1[0]]
        grid2 = self.stage[pos2[1]][pos2[0]]
        # 그리드의 화면상 위치 교환
        grid1.rect.x, grid2.rect.x = grid2.rect.x, grid1.rect.x
        grid1.rect.y, grid2.rect.y = grid2.rect.y, grid1.rect.y
        # stage 리스트에서 그리드 객체 교환
        self.stage[pos1[1]][pos1[0]], self.stage[pos2[1]][pos2[0]] = self.stage[pos2[1]][pos2[0]], self.stage[pos1[1]][pos1[0]]
        # 그리드의 배열 내 위치 교환
        grid1.pos_x, grid2.pos_x = grid2.pos_x, grid1.pos_x
        grid1.pos_y, grid2.pos_y = grid2.pos_y, grid1.pos_y

    def check_matches(self):
        matches = set()  # 매치된 그리드 위치를 저장할 집합
        for y in range(self.height):
            for x in range(self.width):
                # 가로 방향으로 3개 연속 매치 확인
                if x < self.width - 2 and self.stage[y][x].type == self.stage[y][x + 1].type == self.stage[y][x + 2].type:
                    matches.update({(x, y), (x + 1, y), (x + 2, y)})
                # 세로 방향으로 3개 연속 매치 확인
                if y < self.height - 2 and self.stage[y][x].type == self.stage[y + 1][x].type == self.stage[y + 2][x].type:
                    matches.update({(x, y), (x, y + 1), (x, y + 2)})
        return matches

    def remove_matches(self, matches):
        for x, y in matches:
            # 매치된 그리드의 타입을 None으로 설정하여 제거
            self.stage[y][x].type = None

    def drop_items(self):
        for x in range(self.width):
            for y in range(self.height - 1, -1, -1):
                # 빈 그리드를 찾으면
                if self.stage[y][x].type is None:
                    # 그 위의 그리드를 아래로 떨어뜨림
                    for k in range(y - 1, -1, -1):
                        if self.stage[k][x].type is not None:
                            self.stage[y][x].type = self.stage[k][x].type
                            self.stage[y][x].surface = self.stage[k][x].surface
                            self.stage[k][x].type = None
                            break

    def refill(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.stage[y][x].type is None:
                    # 빈 그리드를 새로운 랜덤 타입으로 채움
                    self.stage[y][x].type = random.choice(self.foodlist)
                    # 새 타입에 맞는 이미지를 로드하고 크기를 조정함
                    img_path = os.path.join(r"C:\nong\img", f'{self.stage[y][x].type}.jpg')
                    self.stage[y][x].surface = pygame.image.load(img_path)
                    self.stage[y][x].surface = pygame.transform.scale(self.stage[y][x].surface, (60, 60))

    def resolve_matches(self):
        while True:
            # 현재 매치된 그리드를 확인
            matches = self.check_matches()
            if not matches:
                break
            # 매치된 그리드를 제거하고, 빈 공간을 채움
            self.remove_matches(matches)
            self.drop_items()
            self.refill()

class Grid(pygame.sprite.Sprite):
    def __init__(self, x, y, pos_x, pos_y, t):
        # Pygame의 Sprite 클래스를 초기화합니다.
        pygame.sprite.Sprite.__init__(self)
        
        # 그리드 셀에 사용할 이미지 파일의 경로를 생성합니다.
        img_path = os.path.join(r"C:\nong\img", f'{t}.jpg')
        
        try:
            # 이미지 파일을 로드하고 크기를 60x60으로 변환합니다.
            self.surface = pygame.image.load(img_path)
            self.surface = pygame.transform.scale(self.surface, (60, 60))
        except pygame.error as e:
            # 이미지 로드 중 오류가 발생한 경우, 기본 빨간색 Surface를 생성합니다.
            print(f"Error loading image {img_path}: {e}")
            self.surface = pygame.Surface((60, 60))
            self.surface.fill((255, 0, 0))
        except FileNotFoundError as e:
            # 이미지 파일을 찾을 수 없는 경우, 기본 빨간색 Surface를 생성합니다.
            print(f"File not found: {img_path}")
            self.surface = pygame.Surface((60, 60))
            self.surface.fill((255, 0, 0))
        
        # 그리드 셀의 타입을 설정합니다.
        self.type = t
        
        # 그리드 셀의 위치와 크기를 나타내는 Rect 객체를 설정합니다.
        self.rect = self.surface.get_rect()
        
        # 그리드 배열에서의 위치(인덱스)를 설정합니다.
        self.pos_x = pos_x
        self.pos_y = pos_y
        
        # 그리드 셀의 화면상 좌표를 설정합니다.
        self.rect.x = x
        self.rect.y = y

class Game:
    def __init__(self):
        print("Initializing game...")
        # Pygame 라이브러리 초기화
        pygame.init()
        # Pygame의 오디오 시스템 초기화
        pygame.mixer.init()
        # 게임 창의 제목 설정
        pygame.display.set_caption("CookingCrush!")
        # 게임 창의 크기 설정 (800x960)
        self.screen = pygame.display.set_mode((800, 960))
        # FPS 관리를 위한 시계 객체 생성
        self.clock = pygame.time.Clock()
        # Stage 객체 초기화 (8x9 그리드, 'h', 'c', 'p', 'o', 't', 's' 타입)
        self.stage = Stage(8, 9, ['h', 'c', 'p', 'o', 't', 's'])
        # 첫 번째 클릭 위치 초기화
        self.first_click = None
        print("Game initialized.")

    def run(self):
        print("Starting game loop...")
        # 게임 루프를 실행할 변수 설정
        running = True
        # 초기 매칭 제거
        self.stage.resolve_matches()
        
        while running:
            # 이벤트 처리 루프
            for event in pygame.event.get():
                # 게임 종료 이벤트 처리
                if event.type == pygame.QUIT:
                    running = False
                # 마우스 클릭 이벤트 처리
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            # 화면을 흰색으로 채움
            self.screen.fill((255, 255, 255))

            # 모든 그리드를 화면에 그림
            for row in self.stage.stage:
                for grid in row:
                    self.screen.blit(grid.surface, grid.rect)

            # 화면 업데이트
            pygame.display.flip()
            # 프레임 속도 조절 (60 FPS)
            self.clock.tick(60)

        print("Exiting game loop...")
        # Pygame 종료
        pygame.quit()

    def handle_click(self, pos):
        # 클릭한 위치를 그리드 인덱스로 변환
        grid_x = (pos[0] - self.stage.x) // 65
        grid_y = (pos[1] - self.stage.y) // 65
        
        # 그리드 인덱스가 유효한 범위 내에 있는지 확인
        if 0 <= grid_x < self.stage.width and 0 <= grid_y < self.stage.height:
            # 현재 클릭 위치 저장
            current_click = (grid_x, grid_y)
            # 첫 번째 클릭인 경우
            if self.first_click is None:
                self.first_click = current_click
            else:
                # 첫 번째 클릭과 다른 위치를 클릭했을 때
                if self.first_click != current_click:
                    # 그리드 교환 시도
                    self.stage.swap(self.first_click, current_click)
                    # 매치가 있는지 확인
                    if self.stage.check_matches():
                        # 매치를 제거하고 새로 채우기
                        self.stage.resolve_matches()
                    else:
                        # 매치가 없으면 다시 원상 복구
                        self.stage.swap(self.first_click, current_click)
                    # 첫 번째 클릭 초기화
                    self.first_click = None
        else:
            # 유효하지 않은 클릭 위치 출력
            print(f"Invalid click position: ({grid_x}, {grid_y})")
            self.first_click = None

if __name__ == "__main__":
    print("Starting program...")
    # Game 객체 생성 및 실행
    game = Game()
    game.run()
    print("Program terminated.")
