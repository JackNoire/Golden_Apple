#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
import math
import time
import random
import sys

import os
# If the code is frozen, use this path:
if getattr(sys, 'frozen', False):
    CurrentPath = sys._MEIPASS
# If it's not use the path we're on now
else:
    CurrentPath = os.path.dirname(__file__)
# Look for the 'data' folder on the path I just gave you:
dataPath = os.path.join(CurrentPath, 'data')

pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.init()
screen = pygame.display.set_mode((500, 600))
pygame.display.set_caption("Golden Apple")
#加载图片
appleimg = pygame.image.load(os.path.join(dataPath, 'apple.png')).convert_alpha()
personimg = []
for i in range(6):
    personimg.append(pygame.image.load(os.path.join(dataPath, 'tamiao') + str(i) + '.png').convert_alpha())
backgroundimg = pygame.image.load(os.path.join(dataPath, 'background.png')).convert()
bowimg = pygame.image.load(os.path.join(dataPath, 'bow.png')).convert_alpha()
diamondimg = []
for i in range(3):
    diamondimg.append(pygame.image.load(os.path.join(dataPath, 'diamond') + str(i) + '.png').convert_alpha())
platformimg = pygame.image.load(os.path.join(dataPath, 'platform.png')).convert()
#加载声音
shootSound = pygame.mixer.Sound(os.path.join(dataPath, 'shoot.ogg'))
cutSound = pygame.mixer.Sound(os.path.join(dataPath, 'cut.ogg'))
glassSound = pygame.mixer.Sound(os.path.join(dataPath, 'glass.ogg'))
bounceSound = pygame.mixer.Sound(os.path.join(dataPath, 'bounce.ogg'))


def dist(x1, y1, x2, y2):
    return ((x1 - x2)**2 + (y1 - y2)**2)**0.5

#求向量(x1, y1)通过法向量(x2,y2)对称得到的向量
def vector_symmetry(x1, y1, x2, y2):
    x3 = (2 * y1 * x2 * y2 + x1 * (x2**2 - y2**2)) / (x2**2 + y2**2)
    y3 = (2 * x1 * x2 * y2 - y1 * (x2**2 - y2**2)) / (x2**2 + y2**2)
    return x3, y3

class apple(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 12.5
        self.vx = 0;
        self.vy = 0;
        self.img = appleimg
    
    def collidepoint(self, x, y = None):
        if y == None:
            return dist(self.x, self.y, x[0], x[1]) <= self.r
        else:
            return dist(self.x, self.y, x, y) <= self.r
    
    def colliderect(self, rect):
        c = rect.center
        p = [self.x, self.y]
        cp = [abs(p[0] - c[0]), abs(p[1] - c[1])]
        h = [rect.width / 2, rect.height / 2]
        u = [cp[0] - h[0], cp[1] - h[1]]
        u_new = [u[0] if u[0] > 0 else 0, u[1] if u[1] > 0 else 0]
        if dist(u_new[0], u_new[1], 0, 0) > self.r:
            return self.vx, self.vy
        if u[0] <= 0:
            return self.vx, -self.vy
        if u[1] <= 0:
            return -self.vx, self.vy
        u[0] *= 1 if p[0] > c[0] else -1
        u[1] *= 1 if p[1] > c[1] else -1
        return vector_symmetry(self.vx, self.vy, u[1], -u[0])
        
    def copy(self):
        newApple = apple(self.x, self.y)
        newApple.vx = self.vx
        newApple.vy = self.vy
        return newApple
    
    def move_ip(self, deltaX, deltaY):
        self.x += deltaX
        self.y += deltaY

class person(pygame.Rect):
    def __init__(self, left, top, vy):
        self.left = left
        self.top = top
        self.width = 24
        self.height = 35
        self.vy = vy
        self.img = personimg
        self.faceleft = False
    
    def copy(self):
        newPerson = person(self.left, self.top, self.vy)
        newPerson.faceleft = self.faceleft
        return newPerson

class arrow(object):
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
    
    #找到箭的尾部坐标
    def find_tail(self, length):
        d = dist(self.vx, self.vy, 0, 0)
        return self.x - length * self.vx / d, self.y - length * self.vy / d

class graph(object):

    def background():
        screen.blit(backgroundimg, (0, 0))
    
    def apple(theObject):
        screen.blit(appleimg, (theObject.x - theObject.r, theObject.y - theObject.r))
    
    def platform(rect):
        for i in range(rect.width // 5):
            screen.blit(platformimg, (rect.x + i * 5, rect.y))
    
    def person(theObject):
        remainder = abs(theObject.left % 4)
        index = 0
        if remainder == 0 or remainder == 2:
            index = 2 if theObject.faceleft else 3
        elif remainder == 1:
            index = 4 if theObject.faceleft else 5
        else:
            index = 0 if theObject.faceleft else 1
        screen.blit(personimg[index], (theObject.left - 16, theObject.top - 10))
    
    #这里传入的是人物角色的对象
    def bow(theObject):
        mousePos = pygame.mouse.get_pos()
        personPos = theObject.center
        if mousePos[0] == personPos[0]:
            degree = 90 if mousePos[1] < personPos[1] else -90
        elif mousePos[0] > personPos[0]:
            degree = math.degrees(math.atan((personPos[1] - mousePos[1]) / (mousePos[0] - personPos[0])))
        else:
            degree = math.degrees(math.atan((personPos[1] - mousePos[1]) / (mousePos[0] - personPos[0]))) + 180
        newBow = pygame.transform.rotate(bowimg, degree)
        bowRect = newBow.get_rect(center = personPos)
        screen.blit(newBow, bowRect)
    
    def diamond(rect):
        i = int(time.time() * 10) % 3
        screen.blit(diamondimg[i], rect)
    
    def arrow(arrowlist):
        for anArrow in arrowlist:
            pygame.draw.line(screen, pygame.Color(0, 0, 0), (anArrow.x, anArrow.y), anArrow.find_tail(15), 2)

#给一回合游戏创建一个类
class round(object):
    Gpup = 0.3      #人物上升重力加速度
    Gpdown = 0.15    #人物下降重力加速度
    Gapple = 0.05   #苹果重力加速度
    def __init__(self, platform1, platform2, thePerson, arrowlist, theApple, diamondleft):
        self.platform1 = pygame.Rect(platform1[0], 200, platform1[1] - platform1[0], 50)
        self.platform2 = pygame.Rect(platform2[0], 400, platform2[1] - platform2[0], 50)
        self.person = thePerson
        self.arrowlist = arrowlist
        self.apple = theApple
        self.diamond = pygame.Rect(diamondleft, 150, 25, 50)
        self.pmoveleft = self.pmoveright = False
        keys = pygame.key.get_pressed();
        if keys[K_a]:
            self.pmoveleft = True
        if keys[K_d]:
            self.pmoveright = True
    
    #对游戏界面物体的物理属性进行更新
    def update(self):
        #更新弓箭位置并计算弓箭碰撞情况，撞上苹果则更新苹果速度
        for anArrow in self.arrowlist:
            anArrow.x += anArrow.vx
            anArrow.y += anArrow.vy
        arrowlength = len(self.arrowlist)
        i = 0
        while i < arrowlength:
            if self.apple.collidepoint(self.arrowlist[i].x, self.arrowlist[i].y):
                self.apple.vx = (self.apple.vx + self.arrowlist[i].vx) / 2
                self.apple.vy = (self.apple.vy + self.arrowlist[i].vy) / 2
                cutSound.play()
                del self.arrowlist[i]
                arrowlength -= 1
                continue
            if self.platform1.collidepoint(self.arrowlist[i].x, self.arrowlist[i].y)  \
            or self.platform2.collidepoint(self.arrowlist[i].x, self.arrowlist[i].y):
                del self.arrowlist[i]
                arrowlength -= 1
                continue
            if self.arrowlist[i].x < 50 or self.arrowlist[i].x > 450    \
            or self.arrowlist[i].y < 50 or self.arrowlist[i].y > 550:
                del self.arrowlist[i]
                arrowlength -= 1
                continue
            i += 1
        #更新人物位置以及竖直速度并考虑是否会碰壁
        newperson = self.person.copy()
        #更新人物竖直速度及位置
        newperson.vy = self.person.vy + self.Gpup if self.person.vy <= 0 else self.person.vy + self.Gpdown
        if newperson.vy > 10:
            newperson.vy = 10
        newperson.move_ip(0, newperson.vy)
        if newperson.colliderect(self.platform1) or newperson.colliderect(self.platform2):
            newperson.move_ip(0, -newperson.vy)
            newperson.vy = 0    
        elif newperson.top <= 50 or newperson.top >= 515:
            newperson.move_ip(0, -newperson.vy)
            newperson.vy = 0
        #更新人物水平位置
        if self.pmoveleft and not self.pmoveright:
            newperson.move_ip(-5, 0)
            newperson.faceleft = True
            if newperson.colliderect(self.platform1) or newperson.colliderect(self.platform2)   \
            or newperson.left <= 50 or newperson.left >= 426:
                newperson.move_ip(5, 0)
        if self.pmoveright and not self.pmoveleft:
            newperson.move_ip(5, 0)
            newperson.faceleft = False
            if newperson.colliderect(self.platform1) or newperson.colliderect(self.platform2)   \
            or newperson.left <= 50 or newperson.left >= 426:
                newperson.move_ip(-5, 0)
        self.person = newperson
        #更新苹果位置并考虑是否会碰壁
        newapple = self.apple.copy()
        newapple.vy = self.apple.vy + self.Gapple
        velocity_transform_function = lambda x : 1 if x > 0 else -1
        newapple.vx = newapple.vx if abs(newapple.vx) < 5 else 5 * velocity_transform_function(newapple.vx)
        newapple.vy = newapple.vy if abs(newapple.vy) < 5 else 5 * velocity_transform_function(newapple.vy)
        newapple.move_ip(newapple.vx, newapple.vy)
        #先考虑与四周墙壁的碰撞
        if newapple.x <= 62.5 or newapple.x >= 437.5:
            newapple.move_ip(-newapple.vx, -newapple.vy)
            newapple.vx = -newapple.vx
            newapple.move_ip(newapple.vx, newapple.vy)
            bounceSound.play()
        if newapple.y <= 62.5:
            newapple.move_ip(-newapple.vx, -newapple.vy)
            newapple.vy = -newapple.vy
            newapple.move_ip(newapple.vx, newapple.vy)
            bounceSound.play()
        elif newapple.y >= 550:
            return True     #如果苹果掉到下面返回前一回合
        #再考虑与平台的碰撞
        original_vx, original_vy = newapple.vx, newapple.vy
        newapple.vx, newapple.vy = newapple.colliderect(self.platform1)
        newapple.vx, newapple.vy = newapple.colliderect(self.platform2)
        newapple.move_ip(-original_vx, -original_vy)
        newapple.move_ip(newapple.vx, newapple.vy)
        if newapple.vx != original_vx or newapple.vy != original_vy:
            bounceSound.play()
        self.apple = newapple
        return False
    
    #根据产生的事件类型进行调整，控制人物行动
    def control(self, event):
        if event.type == KEYDOWN:
            if event.key == K_a:
                self.pmoveleft = True
            elif event.key == K_d:
                self.pmoveright = True
            elif event.key == K_w:
                self.person.vy = -7
        elif event.type == KEYUP:
            if event.key == K_a:
                self.pmoveleft = False
            elif event.key == K_d:
                self.pmoveright = False
        elif event.type == MOUSEBUTTONDOWN:
            if len(self.arrowlist) >= 10:
                return None
            mousePos = pygame.mouse.get_pos()
            personPos = self.person.center
            hypotenuse = dist(mousePos[0], mousePos[1], personPos[0], personPos[1])
            anArrow = arrow(personPos[0], personPos[1], 7 * (mousePos[0] - personPos[0]) / hypotenuse, \
            7 * (mousePos[1] - personPos[1]) / hypotenuse)
            self.arrowlist.append(anArrow)
            shootSound.play()
        elif event.type == QUIT:
            sys.exit()
    
    def graph_all(self):
        graph.background()
        graph.platform(self.platform1)
        graph.platform(self.platform2)
        graph.person(self.person)
        graph.bow(self.person)
        graph.apple(self.apple)
        graph.diamond(self.diamond)
        graph.arrow(self.arrowlist)

def one_round(platform1, platform2, thePerson, theApple, diamondleft, roundNum, lastRound):
    thisRound = round(platform1, platform2, thePerson, [], theApple, diamondleft)
    while True:
        gotoPreviousRound = thisRound.update()
        if gotoPreviousRound:
            return False, thisRound.apple
        #如何出现苹果卡进平台的情况则重新弹射苹果
        if thisRound.platform1.collidepoint(thisRound.apple.x, thisRound.apple.y)   \
        or thisRound.platform2.collidepoint(thisRound.apple.x, thisRound.apple.y):
            thisRound.apple = apple(100, 100)
            thisRound.apple.vx = 4
        for event in pygame.event.get():
            thisRound.control(event)
        #绘图
        thisRound.graph_all()
        #打印文字
        font = pygame.font.Font(os.path.join(dataPath, 'consolas.ttf'), 50)
        text_surface = font.render('Round %d' % roundNum, True, (255, 255, 255))
        screen.blit(text_surface, (165, -5))
        if roundNum == lastRound:
            font = pygame.font.Font(os.path.join(dataPath, 'consolas.ttf'), 50)
            text_surface = font.render('Complete!', True, (0, 0, 255))
            screen.blit(text_surface, (150, 200))
        pygame.display.update()
        new_vx, new_vy = thisRound.apple.colliderect(thisRound.diamond)
        if new_vx != thisRound.apple.vx or new_vy != thisRound.apple.vy:
            return True, thisRound.person
        pygame.time.delay(10)

def generate_game(lastRound = 100):
    platform_list = []
    diamond_list = []
    aPlatform = (50, 450)
    aDiamondLeft = -100
    platform_list.append(aPlatform)
    diamond_list.append(aDiamondLeft)
    for i in range(lastRound):
        platformLength = 300 - (i // 2) * 5
        if platformLength < 50:
            platformLength = 50
        platformLeft = random.randint(10, (450 - platformLength) // 5) * 5
        diamondLeft = random.randint(platformLeft, platformLeft + platformLength - 25)
        platform_list.append((platformLeft, platformLeft + platformLength))
        diamond_list.append(diamondLeft)
    platform_list.append((-100, -99))
    diamond_list.append(-100)
    roundNum = 0
    thePerson = person(100, 300, 0)
    theApple = apple(350, 350)
    while True:
        is_next, theObject = one_round(platform_list[roundNum + 1], platform_list[roundNum], \
        thePerson, theApple, diamond_list[roundNum + 1], roundNum, lastRound)
        if is_next:
            glassSound.play()
            theApple.x = diamond_list[roundNum + 1] + 12.5
            theApple.y = 350
            theApple.vx = 0
            theApple.vy = 0
            thePerson = theObject
            thePerson.move_ip(0, 200)
            if thePerson.top > 500:
                thePerson.top = 500
            roundNum += 1
        else:
            roundNum -= 1
            if roundNum != 0:
                thePerson = person(100, 500, 0)
            else:
                thePerson = person(100, 300, 0)
            theApple = theObject
            theApple.y = 70

if __name__ == '__main__':
    generate_game()