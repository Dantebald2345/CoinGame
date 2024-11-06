
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
    minimum_price = 100

    def __init__(self, name, type, deq: deque, change_coeff, price_multiplier, pointer):
        self.name = name
        self.type = type
        self.deq = deq
        self.change_coeff = change_coeff
        self.price_multiplier = price_multiplier
        self.stock_pointer = self.mid
        self.pointer = pointer
        self.current_price = self.mid

    def stock(self, updown=None):
        price_diff = change_price(self.change_coeff, self.stock_pointer, self.start_pos_y, self.end_pos_y, updown)
        if price_diff >= 0:
            self.deq.append((self.stock_pointer, price_diff, (0,0,255))) #blue
        else:
            self.deq.append((self.stock_pointer, price_diff, (255,0,0))) #red
        self.stock_pointer += price_diff
        self.current_price = (self.end_pos_y - self.stock_pointer + self.minimum_price) * self.price_multiplier
        if self.start_pos_x + self.pointer*self.line_interval > self.end_pos_x:
            self.deq.popleft()
        else:
            self.pointer += 1

    def update(self, pygame, screen):
        for i, line in enumerate(self.deq):
            pos_x = self.start_pos_x + i * self.line_interval
            pygame.draw.line(screen, line[2], (pos_x, line[0]), (pos_x, line[0] + line[1]), self.line_width)

    def rect(self, pygame, screen):
        pygame.draw.rect(screen, (255,255,255), (self.start_pos_x-self.border_x, self.start_pos_y-self.border_y, 
            self.end_pos_x-self.start_pos_x+self.border_x*2, self.end_pos_y-self.start_pos_y+self.border_y*2))
        pygame.draw.line(screen, "#000000", (self.start_pos_x-self.line_width/2, self.start_pos_y), (self.start_pos_x-self.line_width/2, self.end_pos_y), 2)
        pygame.draw.line(screen, "#000000", (self.start_pos_x-self.line_width/2, self.end_pos_y), (self.end_pos_x, self.end_pos_y), 2)


def change_price(coeff, current, min, max, updown:int):
    sum = 0
    change_base = 0
    if updown == 1:
        while sum < min or sum > max:
            change_base = random.randrange(-coeff/2, 0)
            sum = current + change_base
    elif updown == 2:
        while sum < min or sum > max:
            change_base = random.randrange(0, coeff/2)
            sum = current + change_base
    else:
        while sum < min or sum > max:
            change_base = random.randrange(-coeff, coeff)
            sum = current + change_base
    return change_base
