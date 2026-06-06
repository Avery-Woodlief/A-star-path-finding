from navigator import *

import pygame
from random import randint
import json
import re

pygame.init()

#map_name = "obstacle_course1.json"

with open(f"{input('choose a map: ')}.json", "r") as file:
    world_map = json.load(file)

#print(world_map)



rect_args = None
color_args = None

obstacles = {}

for r, c in world_map.items():
    a1 = re.findall(r"\d+", r)
    a1_map = map(int, a1)
    rect_args = []
    for i in a1_map:
        rect_args.append(i)
    topleft = (rect_args[0], rect_args[1])
    size = (rect_args[2], rect_args[3])
    a2 = re.findall(r"\d+", c)
    a2_map = map(int, a2)
    color_args = []
    for i in a2_map:
        color_args.append(i)

    obstacles[Obstacle(topleft, size)] = tuple(color_args)
    #obstacles.append(Obstacle(topleft, size))





color_pool = {
                0 : "white",
                1 : "red",
                2 : "green",
                3 : "blue",
                4 : "black"          
             }

colors = {
            "white" : pygame.Color(255, 255, 255),
            "red" : pygame.Color(255, 0, 0),
            "green" : pygame.Color(0, 255, 0),
            "blue" : pygame.Color(0, 0, 255),
            "black" : pygame.Color(0, 0, 0)
        }

screen = pygame.display.set_mode((1000, 800))
pygame.display.set_allow_screensaver(True)


screen.fill(colors["white"])



nav = None
start = None
end = None
stop_drawing = False
running = True
while (running):

    for obstacle, color in obstacles.items():
        pygame.draw.rect(screen, color, obstacle)

    for event in pygame.event.get():
        if (event.type == pygame.WINDOWLEAVE):
            print("No come back!")
        if (event.type in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN]):
            #print("mouse event")
            '''
            if (event.type == pygame.MOUSEMOTION):
                print(event.pos)
            '''
            if (event.type == pygame.MOUSEBUTTONDOWN):
                if (event.button == 3):
                    end = event.pos
                elif (event.button == 1):
                    start = event.pos
                if (not end):
                    continue
                if (not start):
                    continue
                if (stop_drawing):
                    continue
                nav = Navigator(start, end, list(obstacles.keys()))
                pygame.draw.circle(screen, colors["blue"], start, 5)
                counter = 0
                if (nav):
                    while (not (nav.start == nav.target)):
                        prev = nav.current.point

                        if (counter < 100):
                            nav.step(stride = 5)
                            counter += 1
                        else:
                            nav.step()
                        #print(nav.current)
                        
                        pygame.draw.circle(screen, colors[color_pool[randint(2, 3)]], nav.current.point, 5)
                        #pygame.draw.line(screen, colors["green"], prev, nav.current.point, width = 2)                        
                        pygame.display.flip()
                        if (nav.current == nav.target):
                            break
                nav = None
                print("completed path")
                
        if (event.type in [pygame.KEYDOWN, pygame.KEYUP]):
            if (event.key == pygame.K_ESCAPE):
                running = False
            if (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_s):
                    stop_drawing = not stop_drawing
                    if (stop_drawing):
                        print("stopped drawing!")
                    else:
                        print("started drawing!")
        elif (event.type == pygame.QUIT):
            running = False
    pygame.display.flip()

pygame.quit()

