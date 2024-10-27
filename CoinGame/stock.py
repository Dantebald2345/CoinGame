import random
from collections import deque
class Stock():

    start_pos_x = 100  # 주식 그래프
    start_pos_y = 100  # 직사각형 경계
    end_pos_x = 680    # 크기 설정하는
    end_pos_y = 370    # 상수
    border_x = 50             # 그래프 칸
    border_y = border_x*0.75  # 설정하는 상수
    mid = (start_pos_y + end_pos_y)/2
    line_width = 5
    line_interval = line_width + 1

    def __init__(self, deq: deque, change_coeff, price_multiplier, pointer):
        self.deq = deq
        self.change_coeff = change_coeff
        self.price_multiplier = price_multiplier
        self.stock_pointer = self.mid
        self.pointer = pointer

    def stock(self):
        price_diff = change_price(self.change_coeff, self.stock_pointer, self.start_pos_y, self.end_pos_y)
        if price_diff >= 0:
            self.deq.append((self.stock_pointer, price_diff, (0,0,255)))
        else:
            self.deq.append((self.stock_pointer, price_diff, (255,0,0)))
        self.stock_pointer += price_diff
        if self.start_pos_x + self.pointer*self.line_interval > self.end_pos_x:
            self.deq.popleft()
        else:
            self.pointer += 1

    def update(self, pygame, screen):
        for i in range(len(self.deq)): #그래프 그리기
            line = self.deq[i]
            pos_x = self.start_pos_x + i*self.line_interval
            pygame.draw.line(screen, line[2], (pos_x, line[0]), (pos_x, line[0]+line[1]), self.line_width)

    def rect(self, pygame, screen):
        pygame.draw.rect(screen, (255,255,255), (self.start_pos_x-self.border_x, self.start_pos_y-self.border_y, 
            self.end_pos_x-self.start_pos_x+self.border_x*2, self.end_pos_y-self.start_pos_y+self.border_y*2))        


def change_price(coeff, current, min, max):
    sum = 0
    change_base = 0
    while sum < min or sum > max:
        change_base = random.randrange(-coeff, coeff)
        sum = current + change_base

    return change_base
