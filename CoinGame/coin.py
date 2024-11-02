import os
import sys
import pygame
import cv2
import random
import json
from pygame.constants import QUIT
from collections import deque
from stock import Stock
from button import Button

pygame.init()

screen_width = 1280
screen_height = 720
SCREEN = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("CoinGame")

current_path = os.path.dirname(__file__)     
image_path = os.path.join(current_path, "images")
font_path = os.path.join(current_path, "font")
background = pygame.transform.scale(pygame.image.load(os.path.join(image_path, "background.png")), (1280, 1280))
background_animated = os.path.join(image_path, "background.mp4")

# OpenCV 비디오 캡처 생성
cap = cv2.VideoCapture(background_animated)
if not cap.isOpened():
    print("Error: Could not open video file.")
    sys.exit()  # 만약 열리는데 실패했다면 터미널에 실패 표시

# fps 설정
clock = pygame.time.Clock()
fps = 60
rankings_file = os.path.join(current_path, "rankings.json")

def get_font(i, size):
    fonts = [0, "font.ttf", "DNFBitBitv2.ttf"]
    return pygame.font.Font(os.path.join(font_path, fonts[i]), size)

def play_mp4_cv():
    ret, frame = cap.read()  # 비디오 프레임 읽기
    if not ret or frame is None:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 비디오가 끝나면 처음부터 다시 반복시키기
        ret, frame = cap.read()
        if frame is None:
            print("Error: Could not read video frame.")
            sys.exit()  # 프로그램 종료

    frame = cv2.resize(frame, (screen_width, screen_height))  # 프레임을 화면 크기에 맞게 조정
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # BGR에서 RGB로 변환
    frame = pygame.surfarray.make_surface(frame)  # OpenCV 프레임을 Pygame 표면으로 변환
    return frame

def nickname_input():
    nickname = ''
    input_active = True
    font = get_font(2, 50)

    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    nickname = nickname[:-1]
                else:
                    nickname += event.unicode
        
        SCREEN.blit(background, (0, 0))
        nickname_text = font.render("이름을 입력하세요:", True, "White")
        SCREEN.blit(nickname_text, (screen_width // 2 - nickname_text.get_width() // 2, screen_height // 2 - 50))

        entered_nickname_text = font.render(nickname, True, "White")
        SCREEN.blit(entered_nickname_text, (screen_width // 2 - entered_nickname_text.get_width() // 2, screen_height // 2 + 20))

        pygame.display.update()

    return nickname

if os.path.exists(rankings_file):
    os.remove(rankings_file)

def start():  # 시작 메뉴
    running = True

    TITLE_TEXT = get_font(1, 100).render("COIN GAME", True, "#585391")
    TITLE_RECT = TITLE_TEXT.get_rect(center=(640, 150))
    PLAY_BUTTON = Button(None, (640, 330), "시작", get_font(2, 75), '#585391', "White")

    while running:
        clock.tick(fps)

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(mouse_pos):
                    nickname = nickname_input()
                    game(nickname)
                    break

        frame = play_mp4_cv()
        SCREEN.blit(pygame.transform.rotate(frame, -90), (0, 0))

        SCREEN.blit(TITLE_TEXT, TITLE_RECT)
        PLAY_BUTTON.changeColor(mouse_pos)
        PLAY_BUTTON.update(SCREEN)
        pygame.display.update()

# time 타이머 이벤트 설정
TIME_UPDATE = pygame.USEREVENT + 2
pygame.time.set_timer(TIME_UPDATE, 1000)  # 1초(1000ms)마다 이벤트 발생

def save_ranking(nickname, balance):
    ranking_data = []
    if os.path.exists(rankings_file):
        with open(rankings_file, 'r') as f:
            ranking_data = json.load(f)
    
    ranking_data.append({"nickname": nickname, "balance": balance})
    ranking_data = sorted(ranking_data, key=lambda x: x["balance"], reverse=True)[:10]  # 상위 10명만 저장
    
    with open(rankings_file, 'w') as f:
        json.dump(ranking_data, f)

def show_rankings(nickname, balance):
    save_ranking(nickname, balance)  # 현재 플레이어의 기록을 저장

    with open(rankings_file, 'r') as f:
        rankings = json.load(f)
    
    SCREEN.fill((0, 0, 0))
    title_text = get_font(1, 80).render("Ranking", True, "White")
    title_rect = title_text.get_rect(center=(screen_width // 2, 80))
    SCREEN.blit(title_text, title_rect)

    home_button = Button(None, (640, 600), "처음으로", get_font(2, 50), '#585391', "White")

    for i, record in enumerate(rankings):
        rank_text = f"{i + 1}. {record['nickname']}: ${record['balance']}"
        rank_display = get_font(1, 35).render(rank_text, True, "White")
        SCREEN.blit(rank_display, (screen_width // 2 - 250, 150 + i * 40))

    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if home_button.checkForInput(pygame.mouse.get_pos()):
                    waiting = False
                
        home_button.update(SCREEN)
        pygame.display.update()

def show_holdings(owned_stocks, stocks):
    SCREEN.fill((0, 0, 0))
    holdings_title = get_font(2, 50).render("보유 주식 현황", True, "White")
    SCREEN.blit(holdings_title, (screen_width // 2 - holdings_title.get_width() // 2, 50))

    for i, stock in enumerate(stocks):
        stock_name = stock.name
        quantity = owned_stocks[i]
        total_value = quantity * stock.current_price
        holdings_text = f"{stock_name}: {quantity} 주, 총 가치: ${total_value}"
        holdings_display = get_font(2, 35).render(holdings_text, True, "White")
        SCREEN.blit(holdings_display, (screen_width // 2 - holdings_display.get_width() // 2, 150 + i * 40))

    close_button = Button(None, (screen_width // 2, 600), "닫기", get_font(2, 50), '#585391', "White")
    pygame.display.update()

    showing_holdings = True
    while showing_holdings:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if close_button.checkForInput(pygame.mouse.get_pos()):
                    showing_holdings = False  # Close the holdings view

        close_button.update(SCREEN)
        pygame.display.update()

def game(nickname):
    running = True
    balance = 10000

    #주식
    stock_names = [["MK하이닉스", "삼선정자"], ["도기코인", "비츠코인"], ["반짝이는 금", "에메랄드"]]
    stock_types = ["주식", "코인", "광물"]
    stocks = [Stock(random.choice(stock_names[i]), stock_types[i], deque(), random.randint(30, 50), random.randint(100, 200), 0) for i in range(3)]
    stock_to_show = 0
    owned_stocks = [0, 0, 0]

    STOCK_TIMER = pygame.USEREVENT + 1  #주식 업데이트 타이머
    pygame.time.set_timer(STOCK_TIMER, 500) #주기 (단위:ms)

    #주식 전환 버튼
    button_top_margin = 0
    button_interval = 50
    button_length = ((Stock.end_pos_x - Stock.start_pos_x) - button_interval*2) / 3
    button_pos_y = Stock.end_pos_y + button_top_margin + button_length*0.75
    button1_pos = (Stock.start_pos_x + button_length/2, button_pos_y)
    button2_pos = (Stock.start_pos_x + button_length*1.5 + button_interval, button_pos_y)
    button3_pos = (Stock.start_pos_x + button_length*2.5 + button_interval*2, button_pos_y)

    button_poses = [button1_pos, button2_pos, button3_pos]
    stock_buttons = [Button(None, button_poses[i], f"{stocks[i].name}", get_font(2, 30), '#585391', "White") for i in range(3)]

    buy_button = Button(None, (1100, 500), "구매", get_font(2, 50), '#28a745', "White")
    sell_button = Button(None, (1100, 600), "판매", get_font(2, 50), '#dc3545', "White")
    holdings_button = Button(None, (200, 650), "보유 주식", get_font(2, 50), '#585391', "White")

    time = 20

    #속보
    news_rect_height = 70
    news_rect_width = 1000
    news_rect_d_from_left_edge = 50
    news_rect_pos_x = news_rect_d_from_left_edge
    news_rect_pos_y = 550
    NEWS_RECT = pygame.transform.scale(pygame.image.load(os.path.join(image_path, "news_rect.png")), (news_rect_width, news_rect_height))
    news_breaking_pos_x_center = 90
    NEWS_BREAKING_TEXT = get_font(2, 30).render("속보", True, '#000000')
    NEWS_BREAKING_RECT = NEWS_BREAKING_TEXT.get_rect(center=(news_breaking_pos_x_center, news_rect_pos_y+news_rect_height/2))
    megaphone_height = news_rect_height*0.8
    megaphone_pos_x = NEWS_BREAKING_RECT.width/2 + news_breaking_pos_x_center + 10
    MEGAPHONE = pygame.transform.scale(pygame.image.load(os.path.join(image_path, "megaphone.png")), (megaphone_height*4.7/3.7, megaphone_height))

    newss = ["전세계 물류의 약 45%가 지나가는 수에즈 운하가 산사태에 의해 봉쇄되었습니다. 전문가들은 이 현상이 세계 반도체 시장에 미칠 영향을 우려하고 있습니다.",
             "수에즈 운하 봉쇄에 의해 변경된 경로 반경 10km 내에 해적이 살고 있다는 소문이 있습니다. 이 루머의 진위는 아직 밝혀지지 않았지만 선박들은 최첨단 레이저 무기를 갖추고 있어 해적들 쯤은 거뜬히 처리해낼 수 있을 것으로 보입니다.",
             "전세계 희귀 광물 공급량의 약 70%를 담당하고 있는 조선 광산에서 대규모 반제국주의 파업 행위가 일어났습니다. 일제는 진압을 위해 무력을 동원했지만 시위가 끝날 기미는 보이지 않습니다.",
             "뿌에엙!                                                                                                    방송 사고로 인해 의도하지 않은 소음이 송출된 점 사과드립니다.",
             "캄보디아 연구원들이 소량의 금속 샘플을 적은 비용으로 증식시키는 방법을 찾아냈습니다. 네이처(온라인학술자료플랫폼) 회원들은 해당 논문을 검증하는 중이라고 합니다."]
    news_text_rect = pygame.Rect(megaphone_pos_x+megaphone_height*4.7/3.7 + 10, news_rect_pos_y, news_rect_width-170, NEWS_RECT.get_rect().bottom) #3번째 매개변수에 -170은 수식 생각하기 귀찮아서 한거임 알아서 조절하셈!!
    news_speed = 3
    NEWS_TEXT = get_font(2, 25).render(newss[1], True, '#000000')
    news_pos = [1100, news_rect_pos_y+15]

    #제한시간 타이머
    time = 30 #제한시간 (단위:s)
    time_text: str
    timer_pos_x = 1060
    timer_pos_y = 30
    timer_length = 185
    timer_height = 50

    # 깜빡거리는 효과
    blinking = False
    blink_time = 0

    while running:
        clock.tick(fps)
        mouse_pos = pygame.mouse.get_pos()
        news_pos[0] -= news_speed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()

            elif event.type == STOCK_TIMER: #그래프 수치 생성, 저장
                for stock in stocks:
                    stock.stock()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, btn in enumerate(stock_buttons):
                    if btn.checkForInput(mouse_pos):
                        stock_to_show = i

                if buy_button.checkForInput(mouse_pos):
                    current_price = stocks[stock_to_show].current_price / 50
                    if balance >= current_price:
                        balance -= current_price
                        owned_stocks[stock_to_show] += 1

                if sell_button.checkForInput(mouse_pos):
                    if owned_stocks[stock_to_show] > 0:
                        balance += stocks[stock_to_show].current_price / 50
                        owned_stocks[stock_to_show] -= 1

                if holdings_button.checkForInput(mouse_pos):
                    show_holdings(owned_stocks, stocks)

            elif event.type == TIME_UPDATE:
                time -= 1  
                if time <= 0:
                    running = False  

                # Start blinking when time is 5 seconds or less
                if time <= 10:
                    blinking = not blinking  # Toggle blinking state
                    blink_time += 1  # Increment blink timer
                    if blink_time >= 5:  # Blink every 5 frames
                        blink_time = 0  # Reset blink timer

        if time <= 0:
            quantity=0
            total_value=0
            for i in range(3):
                quantity += owned_stocks[i]
                total_value += quantity * stock.current_price
            show_rankings(nickname, round(balance+total_value))
            break

        time_text = f"{(time//60):02}:{(time%60):02}"
        TIME_TEXT = get_font(1, 35).render(time_text, True, "White")
        TIME_RECT = TIME_TEXT.get_rect(center=(timer_pos_x+timer_length/2, timer_pos_y+timer_height/2))                
        
        #배경
        frame = play_mp4_cv()
        SCREEN.blit(pygame.transform.rotate(frame, -90), (0, 0))
        
        #주식 그래프
        stocks[stock_to_show].rect(pygame, SCREEN)
        stocks[stock_to_show].update(pygame, SCREEN)

        #유저 정보
        user_info_text = get_font(2, 35).render(f"이름: {nickname}     |     자산: ${balance}", True, "Black")
        SCREEN.blit(user_info_text, (50, 20))

        #버튼
        for b in stock_buttons + [buy_button, sell_button, holdings_button]:
            b.changeColor(mouse_pos)
            b.update(SCREEN)
        pygame.draw.rect(SCREEN, '#585391', (timer_pos_x, timer_pos_y, timer_length, timer_height))

        #속보
        SCREEN.blit(NEWS_RECT, (news_rect_pos_x, news_rect_pos_y))
        SCREEN.blit(NEWS_BREAKING_TEXT, NEWS_BREAKING_RECT)
        SCREEN.blit(MEGAPHONE, (megaphone_pos_x, news_rect_pos_y+7))
        SCREEN.set_clip(news_text_rect)
        SCREEN.blit(NEWS_TEXT, news_pos)
        SCREEN.set_clip(None)

        #타이머
        # Render the timer text only if not in the blinking state
        if not (time <= 5 and blinking):
            SCREEN.blit(TIME_TEXT, TIME_RECT)

        pygame.display.update()

start()
#game("e")

pygame.quit()
