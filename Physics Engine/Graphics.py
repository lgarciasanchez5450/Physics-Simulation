from time import perf_counter
from pygame import display,draw,Rect,init,time
from pygame import event as events
from pygame.constants import *
from pygame import color
import pygame
from Vectors import *
lim = [-00000,000000]
active_object_pos:Vector2 = Vector2(0)
init()
clock = time.Clock()
def zero():
    return Vector2(0)
Screen_Y = 900//2
Screen_X = 1300//2
Screen_Pos = Vector2(Screen_X,Screen_Y)
def draw_circle(rad:float|int,pos:tuple):
    draw.circle(screen,(255,255,255),pos,rad,1)

planet1 = Celestial_Body(Vector2(0,70),rad = 10,initial_push=random_vector(lim))
planet2 = Celestial_Body(Vector2(0,-70),rad = 10,initial_push=random_vector(lim))
planet3 = Celestial_Body(Vector2(0,-200),rad = 5,initial_push=random_vector(lim))
planet4 = Celestial_Body(Vector2(200,-70),rad = 5,initial_push=random_vector(lim))
planet5 = Celestial_Body(Vector2(-150,90),rad = 5,initial_push=random_vector(lim))
planet6 = Celestial_Body(Vector2(-70,-120),rad = 5,initial_push=random_vector(lim))
sun = Celestial_Body(Vector2(0,0),rad = 20,density=2)
add_Body(sun)
add_Body(planet1)
add_Body(planet2)
add_Body(planet3)
add_Body(planet4)
add_Body(planet5)
add_Body(planet6)
active_object = Celestial_Body() #an empty body located at (0,0) that doesn't move cause it hasn't been "added" yet
from Vectors import planets
#planets.append(planet2)
times = []
screen = display.set_mode((0,0))
while 1:
    mb1down = False
    for event in events.get():
        if event.type == QUIT:
            quit()
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            pos = (Vector2(*pygame.mouse.get_pos())-Screen_Pos+active_object.pos).to_tuple
            body = select_Body(pos)
            if body is not None:
                active_object  = body
    screen.fill((0,0,0))
    for planet in planets:
        planet:Celestial_Body
        draw_circle(planet.rad,(planet.pos+Screen_Pos-active_object.pos).to_tuple)
    #print(active_object_pos)
    update()#1
    #update()#2
    #update()#3
    #update()#4
    #update()#5
    display.flip()
    #clock.tick(144)
