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
    fonts = [0, "font.ttf"]
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
    font = get_font(1, 50)

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
        nickname_text = font.render("Enter your nickname:", True, "White")
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
    PLAY_BUTTON = Button(None, (640, 360), "PLAY", get_font(1, 75), '#585391', "White")

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

    home_button = Button(None, (640, 600), "처음으로", get_font(1, 50), '#585391', "White")

    for i, record in enumerate(rankings):
        rank_text = f"{i + 1}. {record['nickname']}: ${record['balance']}"
        rank_display = get_font(1, 35).render(rank_text, True, "White")
        SCREEN.blit(rank_display, (screen_width // 2 - 200, 150 + i * 40))

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
    holdings_title = get_font(1, 50).render("Current Holdings", True, "White")
    SCREEN.blit(holdings_title, (screen_width // 2 - holdings_title.get_width() // 2, 50))

    for i, stock in enumerate(stocks):
        stock_name = stock.name
        quantity = owned_stocks[i]
        total_value = quantity * stock.current_price
        holdings_text = f"{stock_name}: {quantity} units, Total Value: ${total_value}"
        holdings_display = get_font(1, 35).render(holdings_text, True, "White")
        SCREEN.blit(holdings_display, (screen_width // 2 - holdings_display.get_width() // 2, 150 + i * 40))

    close_button = Button(None, (screen_width // 2, 600), "Close", get_font(1, 50), '#585391', "White")
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

    stock_names = [["MK", "Samsun"], ["Dogi", "Bicz"], ["Gold", "Dia"]]
    stock_types = ["주식", "코인", "광물"]
    stocks = [Stock(random.choice(stock_names[i]), stock_types[i], deque(), random.randint(30, 50), random.randint(100, 200), 0) for i in range(3)]
    stock_to_show = 0
    owned_stocks = [0, 0, 0]

    STOCK_TIMER = pygame.USEREVENT + 1
    pygame.time.set_timer(STOCK_TIMER, 500)  

    button_top_margin = 30
    button_interval = 50
    button_length = ((Stock.end_pos_x - Stock.start_pos_x) - button_interval * 2) / 2
    button_pos_y = Stock.end_pos_y + button_top_margin + button_length * 0.75 - 100
    button1_pos = (Stock.start_pos_x + button_length / 2 - 70, button_pos_y)
    button2_pos = (Stock.start_pos_x + button_length * 1.5 - 70 + button_interval, button_pos_y)
    button3_pos = (Stock.start_pos_x + button_length * 2.5 + button_interval * 2 - 70, button_pos_y)
    stock_buttons = [Button(None, button1_pos, stocks[0].name, get_font(1, 50), '#585391', "White"),
                     Button(None, button2_pos, stocks[1].name, get_font(1, 50), '#585391', "White"),
                     Button(None, button3_pos, stocks[2].name, get_font(1, 50), '#585391', "White")]

    buy_button = Button(None, (1100, 500), "Buy", get_font(1, 50), '#28a745', "White")
    sell_button = Button(None, (1100, 600), "Sell", get_font(1, 50), '#dc3545', "White")
    holdings_button = Button(None, (300, 650), "Holdings", get_font(1, 50), '#585391', "White")

    time = 20
    timer_pos_x = 1060
    timer_pos_y = 70
    timer_length = 185
    timer_height = 50

    # Define the blinking effect variables
    blinking = False
    blink_time = 0

    while running:
        clock.tick(fps)
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()

            elif event.type == STOCK_TIMER:  
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

        time_text = f"{(time // 60):02}:{(time % 60):02}"
        TIME_TEXT = get_font(1, 35).render(time_text, True, "White")
        TIME_RECT = TIME_TEXT.get_rect(center=(timer_pos_x + timer_length / 2, timer_pos_y + timer_height / 2))

        frame = play_mp4_cv()
        SCREEN.blit(pygame.transform.rotate(frame, -90), (0, 0))

        stocks[stock_to_show].rect(pygame, SCREEN)
        stocks[stock_to_show].update(pygame, SCREEN)

        user_info_text = get_font(1, 35).render(f"Nickname: {nickname} | Balance: ${balance}", True, "White")
        SCREEN.blit(user_info_text, (100, 30))

        for b in stock_buttons + [buy_button, sell_button, holdings_button]:
            b.changeColor(mouse_pos)
            b.update(SCREEN)

        pygame.draw.rect(SCREEN, '#585391', (timer_pos_x, timer_pos_y, timer_length, timer_height))

        # Render the timer text only if not in the blinking state
        if not (time <= 5 and blinking):
            SCREEN.blit(TIME_TEXT, TIME_RECT)

        pygame.display.update()

# 시작
start()

# Pygame 종료
pygame.quit()
