from hashlib import new
from math import sqrt
from multipledispatch import dispatch
from random import randint
from time import perf_counter_ns
#from pygame.math import Vector2 as Vec2
class Vector2:
    __slots__ = ('x','y')
    @dispatch(float,int)
    def __init__(self,x,y):
        self.x = x
        self.y = y    
    @dispatch(int,float)
    def __init__(self,x,y):
        self.x = x
        self.y = y
    @dispatch(int, int)
    def __init__(self,x,y):
        self.x = x
        self.y = y
    @dispatch(float, float)
    def __init__(self,x,y):
        self.x = x
        self.y = y
    @dispatch(int)
    def __init__(self,xy):
        self.x = xy
        self.y = xy
    @dispatch(float)
    def __init__(self,xy):
        self.x = xy
        self.y = xy
    @dispatch(object)
    def __add__(self,other):
        x = self.x + other.x
        y = self.y + other.y
        return Vector2(x,y)
    @dispatch(int)
    def __add__(self,other):
        x = self.x + other
        y = self.y + other
        return Vector2(x,y)
        
    @dispatch(float)
    def __add__(self,other):
        x = self.x + other
        y = self.y + other
        return Vector2(x,y)

    @dispatch(int)
    def __radd__(self,other):
        x = self.x + other
        y = self.y + other
        return Vector2(x,y)
    
    @dispatch(float)
    def __radd__(self,other):
        x = self.x + other
        y = self.y + other
        return Vector2(x,y)

    @dispatch(object)
    def __sub__(self,other):
        x = self.x - other.x
        y = self.y - other.y
        return Vector2(x,y)

    @dispatch(int)
    def __sub__(self,other):
        x = self.x - other
        y = self.y - other
        return Vector2(x,y)
    
    @dispatch(object)
    def __mul__(self,other):
        x = self.x * other.x
        y = self.y * other.y
        return Vector2(x,y)

    @dispatch(int)
    def __mul__(self,other):
        x = self.x * other
        y = self.y * other
        return Vector2(x,y)

    @dispatch(float)
    def __mul__(self,other):
        x = self.x * other
        y = self.y * other
        return Vector2(x,y)

    @dispatch(int)
    def __rmul__(self,other):
        x = self.x * other
        y = self.y * other
        return Vector2(x,y)

    @dispatch(float)
    def __rmul__(self,other):
        x = self.x * other
        y = self.y * other
        return Vector2(x,y)
    
    @dispatch(float)
    def __truediv__(self,other):
        x = self.x/other
        y = self.y/other
        return Vector2(x,y)

    @dispatch(int)
    def __truediv__(self,other):
        x = self.x/other
        y = self.y/other
        return Vector2(x,y)

    @dispatch(object)
    def __truediv__(self,other):
        x = self.x/other.x
        y = self.y/other.y
        return Vector2(x,y)

    def rounded(self,n:int):
        return (round(self.x,n),round(self.y,n))

    @property
    def length(self) -> float:
        return sqrt(self.x*self.x+self.y*self.y)

    @property
    def to_tuple(self) -> tuple:
        return (self.x,self.y)

    def __iter__(self):
        return iter((self.x,self.y))
    
    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def copy(self):
        print("COPYING")
        return Vector2(self.x,self.y)
#G = 6.6743e-11
#G = 6.6743e-7
#G = 0.000000000066743
G = .0001
class Celestial_Body:
    pos:Vector2
    vel:Vector2
    accel:Vector2
    rad:float
    density:float
    __slots__  = ('pos','vel','accel','rad','density')
    def __init__(self,pos:Vector2 = Vector2(0),vel:Vector2 = Vector2(0),accel:Vector2 = Vector2(0),rad:float = 1.0,density:float = 1.0, initial_push:Vector2 = Vector2(0)):
        self.pos = pos
        self.vel = vel
        self.accel = accel
        self.rad = rad
        self.density = density
        self.vel += G*initial_push/(rad*rad*density)

    def calc_accel(self,others):
        rad = self.rad
        x,y = self.pos
        mass = rad*rad*self.density
        accelx,accely = 0,0
        for other in others:
            #calculate the force they attract each other with
            other:Celestial_Body
            dx,dy = other.pos.x - x,other.pos.y - y
            mag = G*(other.rad*other.rad*mass*other.density)/(dx*dx + dy*dy)
            accelx += mag*dx
            accely += mag*dy
        self.accel = Vector2(accelx/mass,accely/mass)

    def move(self):
        self.vel += self.accel
        self.pos += self.vel

    def detect_colision(self,others):
        own_mass = self.rad*self.rad*self.density
        for other in others:
            if other.rad > self.rad: #if other mass is greater than own mass
                continue
            other:Celestial_Body
            radii:float = self.rad + other.rad
            dist = other.pos-self.pos
            if dist.length < radii: #if they are colliding
                other_mass = other.rad*other.rad*other.density
                #absorb the other mass into own
                #calculate the mass of both, then add together to get the supposed mass for new, then sqrt to find the rad 
                self.rad = sqrt((other_mass + own_mass) /self.density)
                self.vel += other_mass/own_mass * other.vel
                del planets[planets.index(other)]
                global planet_count,planet_tuple
                planet_count -= 1
                planet_tuple = planet_tuple[:planet_count]

    def __str__(self):
        pos = self.pos.rounded(5)
        vel = self.vel.rounded(5)
        accel = self.accel.rounded(5)
        return f"Pos: {pos}\nVelocity: {vel}\nAcceleration: {accel}"


def update():
    global planets
    for x in planet_tuple:
        planet = planets.pop(x)
        planet.calc_accel(planets)
        planets.insert(x,planet)
    for planet in planets:
        planet.move()
    #for x in planet_tuple:
    #    if x < planet_count:
    #        planet = planets.pop(x)
    #        planet.detect_colision(planets)
    #        planets.insert(x,planet)

planet_tuple = ()      
planets = []
planet_count = 0
def add_Body(new_body:Celestial_Body):
    global planet_count,planet_tuple
    global planets
    planets.append(new_body)
    planet_tuple += (planet_count,)
    planet_count += 1

def select_Body(pos) -> Celestial_Body:
    pos = Vector2(*pos)
    for x in planet_tuple:
        body:Celestial_Body = planets[x]
        dist = pos-body.pos
        if dist.length < body.rad:
            return body
def random_vector(xlimits:list[int],ylimits:list[int] = None):
    if ylimits is None:
        ylimits = xlimits
    x = randint(*xlimits)
    y = randint(*ylimits)
    return Vector2(x,y)

if __name__ == "__main__":
    #testing if for loop is faster or explicitly doing something x time is faster
    from time import perf_counter,perf_counter_ns,time,monotonic
    perf_counter_ns()
    perf_counter()
    a=100
    start = perf_counter_ns()
    [time() for x in range(a)]
    end = perf_counter_ns()
    print(end-start)
    start = perf_counter_ns()
    [monotonic() for x in range(a)]
    end = perf_counter_ns()
    print(end-start)