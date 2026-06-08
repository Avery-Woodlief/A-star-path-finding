from navigator.navigator import *

import pygame
from random import randint
import json
import re
import os

pygame.init()

#map_name = "obstacle_course1.json"

with open(f"maps/{input('choose a map: ')}.json", "r") as file:
    world_map = json.load(file)

#print(world_map)



#rect_args = None
#color_args = None

obstacles = {"Rect":{}, "Circle":{}}

'''
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

    obstacles[ObstacleRect(topleft, size)] = tuple(color_args)
'''


for obstacle_type, instances in world_map.items():
    if (obstacle_type == "Rect"):
        for rect, color in instances.items():
            a1 = re.findall(r"\d+", rect)
            a1_map = map(int, a1)
            rect_args = []
            for i in a1_map:
                rect_args.append(i)
            topleft = (rect_args[0], rect_args[1])
            size = (rect_args[2], rect_args[3])
            a2 = re.findall(r"\d+", color)
            a2_map = map(int, a2)
            color_args = []
            for i in a2_map:
                color_args.append(i)
            obstacles["Rect"][ObstacleRect(topleft, size)] = tuple(color_args)
    elif (obstacle_type == "Circle"):
        for circle, color in instances.items():
            a1 = re.findall(r"\d+", circle)
            a1_map = map(int, a1)
            circle_args = []
            for i in a1_map:
                circle_args.append(i)
            center = (circle_args[0], circle_args[1])
            radius = circle_args[2]
            a2 = re.findall(r"\d+", color)
            a2_map = map(int, a2)
            color_args = []
            for i in a2_map:
                color_args.append(i)
            obstacles["Circle"][ObstacleCircle(center, radius)] = tuple(color_args)

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
            "black" : pygame.Color(0, 0, 0),
            "soft pink": pygame.Color(255, 174, 201),
            "light purple": pygame.Color(127, 0, 127)
        }

screen = pygame.display.set_mode((1000, 800))
pygame.display.set_allow_screensaver(True)


screen.fill(colors["white"])



nav = None
start = None
end = None
stop_drawing = False
running = True


clock = pygame.time.Clock()
nav_log = NavigatorLog(None)



def draw_world(nav, start, end):

    for obstacle_type, instances in obstacles.items():
        if (obstacle_type == "Rect"):
            for rect, color in instances.items():
                pygame.draw.rect(screen, color, rect)
        if (obstacle_type == "Circle"):
            for circle, color in instances.items():
                pygame.draw.circle(screen, color, circle.center, circle.radius)
    '''
    for obstacle, color in obstacles.items():
        pygame.draw.rect(screen, color, obstacle)
    '''

    
    pygame.draw.circle(screen, colors["blue"], start, 5)
    pygame.draw.circle(screen, colors["green"], end, 5)
    #screen.blit(nav.radar_surface, (nav.current.point[0] - nav.search_radius, nav.current.point[1] - nav.search_radius))
    pygame.draw.circle(screen,colors["soft pink"],(nav.center_x, nav.center_y),nav.search_radius,3) # radar
    if (not nav.is_stuck):
        pygame.draw.line(screen, colors["black"], nav.next_point_for_drawing.point, nav.current.point, width=3)
    pygame.draw.circle(screen, colors["light purple"], nav.current.point, 5)
    return

while (running):

    for obstacle_type, instances in obstacles.items():
        if (obstacle_type == "Rect"):
            for rect, color in instances.items():
                pygame.draw.rect(screen, color, rect)
        if (obstacle_type == "Circle"):
            for circle, color in instances.items():
                pygame.draw.circle(screen, color, circle.center, circle.radius)

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
                nav = Navigator(start, end, obstacles)
                #nav_log = NavigatorLog(nav)
                nav_log.change_nav(nav)
                
                if (nav):
                    while (not (nav.start == nav.target)):
                        prev = nav.current.point

                        nav_log.write_step_info()
                        os.system("clear")
                        nav_log.print_to_console()
                        try:
                            nav.step()
                        except (ZeroDivisionError, ValueError):
                            continue
                        
                        if (event.type == pygame.KEYDOWN):
                            if (event.key == pygame.K_c and event.mod & pygame.KMOD_LCTRL):
                                # emergency abort
                                print("aborting current path simulation")
                                break
                        #print(nav.current)

                        screen.fill(colors["white"])

                        draw_world(nav, start, end)
                        #pygame.draw.line(screen, colors["blue"], start, end, width=1)
                        #pygame.draw.line(screen, colors["green"], prev, nav.current.point, width = 2) 
                        clock.tick(60)                 
                        pygame.display.flip()
                        if(dist(nav.current, nav.target) < nav.search_radius/2):#if (nav.current == nav.target):
                            nav_log.write_step_info()
                            nav_log.upload_info()
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
    clock.tick(60)
    pygame.display.flip()

pygame.quit()

