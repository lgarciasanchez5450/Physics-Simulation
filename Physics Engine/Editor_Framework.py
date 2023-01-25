from colors import *
from math import sqrt
#from numba import njit, prange
#from functools import singledispatc
#import numpy as np
from colorsys import *
from random import randint, random
from framework import *
import framework
window_space = Window_Space()

#from pygame.math import Vector2 as Vec2

def toSurfPoints(args):
    positions,selected_body_pos,zoom,simulation_camera_pos = args
    return [((pos.x - selected_body_pos.x)/zoom + simulation_camera_pos.x,(pos.y - selected_body_pos.y)/zoom + simulation_camera_pos.y) for pos in positions]
class Vector2:
    __slots__ = ('x','y')
    def __init__(self,x,y = None):
        self.x = x
        self.y = y if y is not None else x 

    @classmethod
    def random_vector(cls,xmin,xmax,ymin,ymax):
        x = randint(xmin,xmax)
        y = randint(ymin,ymax)
        return cls(x,y)


    def __add__(self,other):
        if isinstance(other,Vector2):
            return Vector2(self.x + other.x,self.y + other.y)
        else:
            return Vector2(self.x + other, self.y + other)

    def __neg__(self):
        return Vector2(-self.x,-self.y)
    
    def __radd__(self,other):
        if isinstance(other,Vector2):
            return Vector2(self.x+other.x,self.y + other.y)
        else:
            return Vector2(self.x + other,self.y + other)

    def __sub__(self,other):
        if isinstance(other,Vector2):
            return Vector2(self.x - other.x, self.y - other.y)
        else:
            return Vector2(self.x - other, self.y - other)


    def dot(self,other) -> float|int:
        x = self.x * other.x
        y = self.y * other.y
        return x+y

    def reflect_across(self,other):
        '''other is assumed to be normalized'''
        return self-2*(self.dot(other))*other #copied from the internet
    
    
    @property
    def normalized(self):
        a = sqrt(self.x * self.x + self.y * self.y)
        return Vector2(self.x/a,self.y/a)

    @property
    def normalize(self) -> None:
        a = self.length
        if a:
            self.x /= a
            self.y /= a
  
    
    def __mul__(self,other):
        if isinstance(other,Vector2):
            return Vector2(self.x * other.x, self.y * other.y)
        else:
            return Vector2(self.x * other,self.y * other)

    def __pow__(self,other:int|float):
        x = self.x ** other
        y = self.y ** other
        return Vector2(x,y)


    def __rmul__(self,other):
        if isinstance(other,Vector2):
            return Vector2(self.x*other.x,self.y*other.y)
        else:
            return Vector2(self.x*other,self.y*other)
    
    def adds(self,*args):
        return sum(args,self)
        x,y = 0,0
        for Vec in args:
            Vec:Vector2
            x += Vec.x
            y += Vec.y
        return Vector2(x,y)

    def __truediv__(self,other):
        x = self.x/other
        y = self.y/other
        return Vector2(x,y)

    def rounded(self,n:int):
        return (round(self.x,n),round(self.y,n))
    
    def make_int(self):
        return (int(self.x),int(self.y))

    @property
    def length(self) -> float|int:
        return sqrt(self.x*self.x+self.y*self.y)

    @property
    def distance_squared(self) -> float|int:
        return self.x * self.x + self.y * self.y

    @property
    def to_tuple(self) -> tuple:
        return (self.x,self.y)

    def __iter__(self):
        return iter((self.x,self.y))
    
    def __str__(self) -> str:
        return f"V: ({self.x}, {self.y})"

    def copy(self):
        return Vector2(self.x,self.y)
    
    def __getitem__(self,index):
        assert isinstance(index,(int,bool)), 'wrong data type to subscript Vector2'
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError('Vector2 object only supports subscripts [0,1]')
    
    def difference(self,other):
        x = self.x - other.x
        y = self.y - other.y
        c = sqrt(x*x+y*y)
        return c
#G = 6.6743e-11 #in scientific notation
#G = 6.6743e-7 # not real 10,000x
#G = 0.000000000066743 #in decimal
G = .00001 #not real
Friction = 1-0.05
MAX_PLANETS = 100
class Celestial_Body:
    x:float
    y:float
    vx:float
    vy:float
    ax:float
    ay:float
    rad:float
    density:float
    mass:float
    unmoveable:bool
    unacceleratable:bool
    color:tuple
    __slots__  = ('x','y','vx','vy','ax','ay','rad','density','name','mass','unmoveable','unacceleratable','color','surface')
    def __init__(self,pos:tuple = (0,0),vel:tuple = (0,0),rad:float = 1.0,density:float = 1.0, name = None,color = (255,255,255), surface = Surface((0,0))):
        self.x, self.y = pos
        self.vx, self.vy = vel
        self.ax, self.ay = (0,0)
        self.rad:float = rad
        self.density:float = density
        self.mass = rad*rad*density
        self.name:str = name if name else str(randint(1,1e23))
        self.unmoveable = False
        self.unacceleratable = False
        self.color = color
        self.surface = surface
        
    def calc_accel(self,others):
        if self.unacceleratable or self.unmoveable: return
        x,y,mass = self.x,self.y,self.mass
        accelx,accely = 0,0
        for other in others:
            if other is self: continue
            other:Celestial_Body
            #calculate the force they attract each other with
            dx,dy =  other.x-x, other.y-y
            dxy = dx*dx+dy*dy
            accelx += dx*other.mass/dxy
            accely += dy*other.mass/dxy
        self.ax, self.ay = G * accelx, G * accely

    def move(self,timeStep):
        if self.unmoveable:return
        if not self.unacceleratable:
            self.vx += self.ax * timeStep
            self.vy += self.ay * timeStep
        self.x += self.vx * timeStep
        self.y += self.vy * timeStep


    def colliding(self,others) -> bool:
        for other in others:
            if other is self:
                continue
            other:Celestial_Body
            radii:float = self.rad + other.rad
            dx, dy = other.x-self.x, other.y - self.y
            dist = sqrt(dx*dx + dy*dy)
            if dist < radii: #if they are colliding
                return True
        return False

    def absorb_colision(self,others:list):
        count = 0
        for other in others:
            if other is self or other.mass > self.mass: #if other mass is greater than own mass
                count += 1
                continue
            other:Celestial_Body
            dx, dy = other.x-self.x, other.y - self.y
            dist = sqrt(dx*dx + dy*dy)
            if dist < self.rad + other.rad: #if they are colliding
                #absorb the other mass into own
                #calculate the mass of both, then add together to get the supposed mass for new, then sqrt to find the rad 
                self.x = (self.x*self.mass + other.x*other.mass)/(self.mass+other.mass)
                self.y = (self.y*self.mass + other.y*other.mass)/(self.mass+other.mass)
                self.vx += Friction*other.mass/self.mass * other.vx
                self.vy += Friction*other.mass/self.mass * other.vy
                self.mass += other.mass
                self.rad = sqrt(self.mass/self.density)
                return count
            count += 1
        

    def bounce_collision(self,others:list):
        if self.unmoveable: return
        for other in others:
            if other is self:
                continue
            other:Celestial_Body
            dx, dy = other.x-self.x, other.y - self.y
            dist = sqrt(dx*dx + dy*dy)
            collision_depth = (self.rad+other.rad-dist)/2
            if  collision_depth > 1e-13: #if they are colliding
                #find difference in pos
                #find center of mass and move both away from that point
                #basically make dist.length == self.rad + other.rad
                dist_x = dx / dist
                dist_y = dy / dist
                if other.unmoveable:
                    self.x -= collision_depth * dist_x * 2
                    self.y -= collision_depth * dist_y * 2
                    own_velocity = Vector2(self.vx,self.vy)
                    collision_normal = Vector2(dx,dy).normalized
                    own_velocity = own_velocity.reflect_across(collision_normal)
                    self.vx,self.vy = own_velocity * Friction
                    return
                self.x -= collision_depth * dist_x
                self.y -= collision_depth * dist_y
                other.x += collision_depth * dist_x
                other.y += collision_depth * dist_y

                m1 = self.mass
                m2 = other.mass
                x = self.x - other.x
                y = self.y - other.y
                d = x * x + y * y

                u1 = (self.vx * x + self.vy * y) / d
                u2 = (x * self.vy - y * self.vx) / d
                u3 = (other.vx * x + other.vy * y) / d
                u4 = (x * other.vy - y * other.vx) / d

                mm = m1 + m2
                vu3 = (m1 - m2) / mm * u1 + (2 * m2) / mm * u3
                vu1 = (m2 - m1) / mm * u3 + (2 * m1) / mm * u1

                other.vx = (x * vu1 - y * u4) * Friction
                other.vy = (y * vu1 + x * u4) * Friction
                self.vx = (x * vu3 - y * u2) * Friction
                self.vy = (y * vu3 + x * u2) * Friction   
                
    def copy(self,silent:bool = True):
        if not silent:
            return Celestial_Body((self.x,self.y),(self.vx,self.vy),self.rad,self.density,self.name+'(Copy)',self.color,self.surface)
        else:
            return Celestial_Body((self.x,self.y),(self.vx,self.vy),self.rad,self.density,self.name,self.color,self.surface)

    def __str__(self):
        return self.name

class Inspector:
    @classmethod
    def accepts(cls) -> tuple:
        return ('mpos','mb1down','KDQueue','mb1up')

    def __new__(cls,pos = None,xsize = None): 
        if not hasattr(cls, 'instance'):
            cls.instance = super(Inspector, cls).__new__(cls)
        return cls.instance


    def __init__(self,pos:tuple,xsize:int):
        self.pos = Vector2(*pos)
        self.object:Celestial_Body = None
        font = makeFont('Arial',14)
        #self.screen_title_pos = TextBox(self.pos)
        self.sim_frames_per_update = 30
        self.pos_setter_x = InputBox((self.pos[0]+5,self.pos[1]+20+20),(xsize-pos[0]-10,16),"X POS",grey,23,self.set_object_x,numbers.union({back_unicode,}),14)
        self.pos_setter_y = InputBox((self.pos[0]+5, self.pos[1]+50+20),(xsize-pos[0]-10,16),'Y POS',grey,23,self.set_object_y,numbers.union({back_unicode,}),14)
        self.pos_title = TextBox((pos[0]+5,pos[1]+4+20),font,"X Pos:",dark_grey)
        self.pos_title_y = TextBox((pos[0]+5,pos[1]+35+20),font,"Y Pos:",dark_grey)
        self.vel_setter_x = InputBox((pos[0]+5,pos[1]+80+20),(xsize-pos[0]-10,16),'X Velocity',grey,23,self.set_object_x_vel,numbers.union({back_unicode,}),14)
        self.vel_title_x = TextBox((pos[0]+5,pos[1]+66+20),font,'X Vel:',dark_grey)
        self.vel_setter_y = InputBox((pos[0]+5,pos[1]+110+20),(xsize-pos[0]-10,16),'Y Velocity',grey,23,self.set_object_y_vel,numbers.union({back_unicode,}),14)
        self.vel_editor = Button((pos[0]+5,pos[1]+150),xsize-pos[0]-10,16,window_space.activateMiniWindow('Vector Editor',1),(80,80,80),(80,80,80),(100,100,100),font.render('Edit Velocity',1,(0,0,0)),50)
        self.vel_title_y = TextBox((pos[0]+5,pos[1]+95+20),font,'Y Vel:',dark_grey)
        self.rad_title = TextBox((pos[0]+5,pos[1]+150+20),font,'Radius:',dark_grey)
        self.rad_setter = InputBox((pos[0]+5,pos[1]+165+20),(xsize-pos[0]-10,16),'Radius',grey,23,self.set_object_attr('rad'),numbers.union({back_unicode,}),14)
        self.density_title = TextBox((pos[0]+5,pos[1]+185+20),font,'Density:',dark_grey)
        self.density_setter = InputBox((pos[0]+5,pos[1]+200+20),(xsize-pos[0]-10,16),'Density',grey,23,self.set_object_attr('density'),numbers.union({back_unicode,}),14)
        self.name_title = TextBox((pos[0]+5,pos[1]-8),font,'Object:',dark_grey)
        self.name_setter = InputBox((pos[0]+5,pos[1]+7),(xsize-pos[0]-10,16),'Name',grey,23,self.set_object_attr('name'),AllCharacters,14)
        self.unmoveable_setter = CheckBox((pos[0]+5,pos[1]+250),17,self.set_object_attr('unmoveable'),(70,70,70),'Unmoveable')
        self.color_title = TextBox((pos[0]+5,pos[1]+290),font,'Color',black)
        self.h_component = Slider(pos[0]+10,pos[1]+315,180,6,0,201,self.set_h_component,light_grey,theme_dark_purple)
        self.s_component = Slider(pos[0]+10,pos[1]+330,180,6,0,201,self.set_s_component,light_grey,dark_grey)
        #self.v_component = Slider(pos[0]+10,pos[1]+345,180,6,0,201,self.set_v_component,light_grey,dark_grey)
        self.hsv = [0,0,1]
        

    def set_h_component(self,newVal) -> None:
        self.hsv[0] = newVal/200
        if self.object:
            self.object.color = hsv_to_rgb(*self.hsv)
            scene.draw_simulation()
    
    def set_s_component(self,newVal) -> None:
        self.hsv[1] = newVal/200
        if self.object:
            self.object.color = hsv_to_rgb(*self.hsv)
            scene.draw_simulation()

    
    def set_v_component(self,newVal) -> None:
        self.hsv[2] = newVal/200
        if self.object:
            self.object.color = hsv_to_rgb(*self.hsv)
            scene.draw_simulation()
    
    def set_scene_and_hierarchy(self,scene,hierarchy) -> None:
        assert isinstance(scene,Editor_Window), 'scene must be of type <Editor_Window>'
        assert isinstance(hierarchy, Hierarchy), 'hierarchy must be of type <Hierarchy>'
        self.scene = scene
        self.hierarchy = hierarchy

    def set_object_x(self,x) -> None:
        try:
            x = float(x)
        except ValueError:
            x = 0
        if self.object:
            self.object.x = x
            scene.draw_simulation()

    def set_object_y(self,y) -> None:
        try:
            y = float(y)
        except ValueError:
            y = 0
        if self.object:
            self.object.y = y
            scene.draw_simulation()

        
    def set_object_x_vel(self,x):
        try:
            x = float(x)
        except ValueError:
            x = 0
        if self.object:
            self.object.vx = x
            scene.draw_simulation()

    def set_object_y_vel(self,y):
        try:
            y = float(y)
        except ValueError:
            y = 0
        if self.object:
            self.object.vy = y
            scene.draw_simulation()

    def set_object_attr(self,attr) -> function:
        def spam(value):
            #assume that every value will have to be converted to float
            if attr != 'name':
                try:
                    value = float(value)
                except ValueError:
                    #default to 0 if anything is wrong
                    value = 0
            if self.object:
                self.object.__setattr__(attr,value)
                scene.draw_simulation()
            if attr == 'name':
                hierarchy.dropdown.recalculate_options()
                window_space.drawBorder('left')
            elif attr == 'density' or attr == 'rad':
                self.object.mass = (self.object.rad**2)*self.object.density
        return spam
    
    def set_vel(self,Vector:Vector2) -> None:
        if self.object:
            self.object.vx, self.object.vy = Vector
            self.vel_setter_x.set_text(str(Vector.x))
            self.vel_setter_y.set_text(str(Vector.y))
            scene.try_draw_vectors()

    def set_object(self,newObject:Celestial_Body) -> None:
        self.object = newObject
        if newObject is None: return
        assert isinstance(newObject,Celestial_Body),"arguement must be of Celestial_Body type"
        self.pos_setter_x.set_text(str(newObject.x))
        self.pos_setter_y.set_text(str(newObject.y))
        self.vel_setter_x.set_text(str(newObject.vx))
        self.vel_setter_y.set_text(str(newObject.vy))
        self.name_setter.set_text(newObject.name)
        self.rad_setter.set_text(str(newObject.rad))
        self.density_setter.set_text(str(newObject.density))
        self.unmoveable_setter.selected = newObject.unmoveable
        self.hsv = list((rgb_to_hsv(*newObject.color)))
        self.h_component.set_value(int(self.hsv[0]*200))
        self.s_component.set_value(int(self.hsv[1]*200))
        #self.v_component.set_value(int(self.hsv[2]*200))


    @property
    def offSetPos(self):
        raise SyntaxError("Use instead <Inspector>._offSetPos")

    @offSetPos.setter
    def offSetPos(self,newVal):
        self._offSetPos = newVal
        self.pos_title.offSetPos = newVal
        self.pos_title_y.offSetPos = newVal
        self.pos_setter_x.offSetPos = newVal
        self.pos_setter_y.offSetPos = newVal
        self.vel_setter_y.offSetPos = newVal
        self.vel_setter_x.offSetPos = newVal
        self.vel_title_x.offSetPos = newVal
        self.vel_title_y.offSetPos = newVal
        self.rad_setter.offSetPos = newVal
        self.rad_title.offSetPos = newVal
        self.density_title.offSetPos = newVal
        self.density_setter.offSetPos = newVal
        self.name_title.offSetPos = newVal
        self.name_setter.offSetPos = newVal
        self.unmoveable_setter.offSetPos = newVal
        self.vel_editor.offSetPos = newVal
        self.h_component.offSetPos = newVal
        self.s_component.offSetPos = newVal
        #self.v_component.offSetPos = newVal
        self.color_title.offSetPos = newVal

    def update(self,things) -> None:
        'mpos,mb1down,kdQueue,mb1up'
        if not self.object: return
        mpos,mb1down,KDQueue,mb1up = things
        f_three = things[:3]
        if scene.running and self.object:
            if not scene.frames%self.sim_frames_per_update:
                self.pos_setter_x.set_text(str(self.object.x))
                self.pos_setter_y.set_text(str(self.object.y))
                self.vel_setter_x.set_text(str(self.object.vx))
                self.vel_setter_y.set_text(str(self.object.vy))
                self.rad_setter.set_text(str(self.object.rad))
                self.density_setter.set_text(str(self.object.density))
        else:
            self.pos_setter_x.update(f_three)
            self.pos_setter_y.update(f_three)
            self.vel_setter_x.update(f_three)
            self.vel_setter_y.update(f_three)
            self.rad_setter.update(f_three)
            self.density_setter.update(f_three)
            self.name_setter.update(f_three)
            self.unmoveable_setter.update(things[:-2])
            self.vel_editor.update([*(things[:2]),0,[],0])
            self.h_component.update((mpos,mb1down,mb1up))
            self.s_component.update((mpos,mb1down,mb1up))
            #self.v_component.update((mpos,mb1down,mb1up))
    
    def draw(self) -> None:
        if not self.object: return
        self.pos_title.draw()
        self.pos_title_y.draw()
        self.pos_setter_x.draw()
        self.pos_setter_y.draw()
        self.vel_setter_y.draw()
        self.vel_setter_x.draw()
        self.vel_title_x.draw()
        self.vel_title_y.draw()
        self.rad_title.draw()
        self.rad_setter.draw()
        self.density_title.draw()
        self.density_setter.draw()
        self.name_setter.draw()
        self.name_title.draw()
        self.unmoveable_setter.draw()
        self.vel_editor.draw()
        self.h_component.draw()
        self.s_component.draw()
        #self.v_component.draw()
        self.color_title.draw()

class Hierarchy:
    @classmethod
    def accepts(cls) -> tuple:
        return ('mpos','mb1down','mb1up','wheel','mb3down')

    def __new__(cls,pos = None,size = None,err_logger=None): 
        if not hasattr(cls, 'instance'):
            cls.instance = super(Hierarchy, cls).__new__(cls)
        return cls.instance
    
    def __init__(self,pos:tuple,size:tuple,err_logger=None):
        self.err_logger = err_logger
        self.object_count_pos_x = pos[0]+size[0]-40
        self.object_count = TextBox((self.object_count_pos_x- len(str(0))*10,pos[1]-22),makeFont('Arial',18,False,True),'0/100',dark_light_grey)
        self.dropdown = Dropdown(pos,(size[0],20),grey,dark_grey,dark_light_grey,scene.planet_names,scene.pick_body,size[1],scene.del_body,(5,0),myfont = makeFont('Courier New',14))

    @property
    def offSetPos(self) -> tuple:
        raise SyntaxError('Use instead <Hierarchy>._offSetPos')

    def set_planet_count(self,num):
        self.object_count.setText(f"{num}/100")
        self.object_count.pos = (self.object_count_pos_x - len(str(num))*10,self.object_count.pos[1])


    @offSetPos.setter
    def offSetPos(self,newVal) -> None:
        self._offSetPos = newVal
        self.dropdown.offSetPos = newVal
        self.object_count.offSetPos = newVal

    def update(self, things):
        '''mpos,mb1down,mb1up,wheel,mb3down'''
        self.dropdown.update(things)

    def draw(self): 
        self.dropdown.draw()
        self.object_count.draw()
    #this class needs to control planet creation and selection

class Editor_Window:
    @classmethod
    def accepts(cls) -> tuple:
        return ('mpos','mb1down','mb1')

    def __new__(cls,pos,size,err_logger = None): #makes this class a singleton object , meaning that this class is restricted to one instance during runtime.
        if not hasattr(cls, 'instance'):
            cls.instance = super(Editor_Window, cls).__new__(cls)
        return cls.instance
    
    __slots__ = ('saved_planets', 'planets', 'planet_count', 'pos', 'size', 'bottom_right', '_rect', 'tools', '_current_tool', 'selected_body', 'surf', 'screen_pos', 'running', 'mpos', 'prev_mpos', '_offSetPos', 'simulation_speed', 'zero', 'zoom', 'started', 'gravity', 'simulation_camera_x','simulation_camera_y', 'state_running', 'state_paused', 'state_stopped', 'active_state', 'moving_body', 'collision_type', 'hierarchy', 'log', 'show_vel', 'show_accel', 'tracing', 'time', 'frames', 'mem_size', 'dots', 'trace_impact', 'accel_exaggeration', 'vel_exaggeration','inspector','hierarchy','OnSelectBody','calculation_type','timeStep')
    def __init__(self,pos,size,err_logger = None):
        self.saved_planets = []
        self.planets:list[Celestial_Body] = []
        self.planet_count = 0
        self.pos = Vector2(*pos)
        self.size = Vector2(*size)
        self.bottom_right = self.pos + self.size
        self._rect = Rect(pos,size)
        self.tools = ('Pan','Select','Move','Place Planet')
        self.current_tool = 3# "Place Planet"
        self.selected_body:Celestial_Body = Celestial_Body()
        self.surf = Surface(size)
        self.screen_pos:tuple = self.pos.to_tuple
        self.running = False
        self.mpos = Vector2(0)
        self.prev_mpos = Vector2(0)
        self._offSetPos = Vector2(0,0)
        self.simulation_speed = 1
        self.zero = Vector2(0)
        self.zoom = 1
        self.started = False
        self.gravity:bool = True
        self.simulation_camera_x = 0
        self.simulation_camera_y = 0
        font = makeFont('Lato',30,0,1)
        self.state_running = font.render("Running",1,(80,120,80))
        self.state_paused = font.render("Paused",1,(100,100,100))
        self.state_stopped = font.render("Stopped",1,(120,80,80))
        self.active_state = self.state_stopped
        self.moving_body:None|Celestial_Body = None
        self.collision_type = 2
        self.log = err_logger
        self.show_vel:bool = True
        self.show_accel:bool = True
        self.tracing:bool = False
        self.time:int = 0
        self.frames:int = 0
        self.mem_size = 100
        self.dots = [[self.zero]*self.mem_size]*self.planet_count
        self.trace_impact = 30
        self.accel_exaggeration = 500_000
        self.vel_exaggeration = 1_000
        self.draw_simulation()
        self.inspector:Inspector
        self.hierarchy:Hierarchy = None
        self.OnSelectBody = self._OnSelectBody
        self.timeStep = 1
        self.calculation_type = 2

    def get_settings(self):
        thingy = f'''
{self.planet_count}
{self.calculation_type}
{self.zoom}
{self.simulation_speed}
{self.timeStep}
{self.current_tool}
{self.tracing}
{G}
        '''
        return thingy
        
    
    def set_calculation_type(self, newVal):
        assert isinstance(newVal,(int,bool)), 'Has to be int or bool'
        self.calculation_type = newVal

    def set_sim_speed(self,newVal):
        try:
            self.simulation_speed = int(newVal)
        except ValueError:
            self.simulation_speed = 1

    def set_trace_impact(self,newVal) -> None:
        try:
            self.trace_impact = int(newVal)
        except ValueError:
            self.trace_impact = 30

    
    def set_mem_size(self,newVal):
        try:
            self.mem_size = int(newVal)
        except ValueError:
            self.mem_size = 100
        for x,planet in enumerate(self.planets):
            self.dots[x] = [(planet.x,planet.y)] * self.mem_size

    def set_show_vel(self,newVal:bool) -> None:
        self.show_vel = newVal
        self.draw_simulation()
    
    def set_show_accel(self,newVal:bool) -> None:
        self.show_accel = newVal
        self.draw_simulation()

    def try_draw_vectors(self):

        self.draw_simulation()
    
    def set_tracing(self,newVal):
        self.tracing = newVal
        if newVal:
            for x,planet in enumerate(self.planets):
                self.dots[x] = [(planet.x,planet.y)]*self.mem_size

    def toSurfPoints(self,positions):
        
        return [((x + self.simulation_camera_x - self.selected_body.x)/self.zoom + self.size.x/2,(y + self.simulation_camera_y - self.selected_body.y)/self.zoom + self.size.y/2) for x,y in positions]


    def draw_arrow(self,vector:Vector2,pos:tuple):
        if isinstance(pos,tuple): #convert pos to Vector2 if neccesary
            pos = Vector2(*pos)
        py_line(self.surf,(0,100,0),pos.to_tuple,pos+vector,2)


    def set_inspector(self,inspector) -> None:
        assert isinstance(inspector,Inspector), 'did not pass the inspector as arg'
        self.inspector = inspector
    def set_hierarchy(self,hierarchy) -> None:
        assert isinstance(hierarchy,Hierarchy), 'did not pass the hierarchy as arg'
        self.hierarchy = hierarchy

    
    def set_tool(self,tool_name:str) -> function:
        assert tool_name in self.tools, 'That tool does not exist!'
        def _():
            self.current_tool = self.tools.index(tool_name)
        return _

    def planet_names(self):
        '''List to iterate over the planet names'''
        return [planet.name for planet in self.planets]

    @property
    def offSetPos(self) -> tuple:
        raise SyntaxError("Do Not use, use instead <Editor_Window>._offSetPos")

    @offSetPos.setter
    def offSetPos(self,newVal):
        difference = Vector2(*newVal)-self._offSetPos
        self._rect.move_ip(*difference.to_tuple)
        self._offSetPos = Vector2(*newVal)
        self.screen_pos = (self.pos+self._offSetPos).to_tuple
        self.size = self.bottom_right - self._offSetPos
        self.surf = Surface(self.size.to_tuple)
        self.draw_simulation()
    
    def set_zoom(self,newVal) -> None:
        self.zoom = newVal
        self.draw_simulation()

    def resize(self,newSize):
        self.size = Vector2(*newSize)
        self.surf = Surface(self.size.to_tuple)
        self.simulation_camera_x = 0
        self.simulation_camera_y = 0
        self.draw_simulation()

    def update_simulation(self):
        planets = self.planets

        if self.gravity:
            for planet in planets:
                planet.calc_accel(planets)

        for planet in planets:
            planet.move(self.timeStep)

        if self.collision_type == 1:
            for x in range(self.planet_count):
                if x < self.planet_count:
                    planet = planets[x]
                    if self.tracing and not self.time%self.trace_impact:
                        self.dots[x].append((planet.x,planet.y))
                        self.dots[x].pop(0)
                    planet_to_del_num = planet.absorb_colision(planets)
                    if planet_to_del_num is not None:
                        self.planets.pop(planet_to_del_num)
                        self.dots.pop(planet_to_del_num)
                        self.planet_count -= 1
        elif self.collision_type == 2:
            for x in range(self.planet_count):
                planet = planets[x]
                if self.tracing and not self.time%self.trace_impact:
                    self.dots[x].append((planet.x,planet.y))
                    self.dots[x].pop(0)
                planet_to_del_num = planet.bounce_collision(planets)  
        else:
            for x in range(self.planet_count):
                    planet = planets[x]
                    if self.tracing and not self.time%self.trace_impact:
                        self.dots[x].append((planet.x,planet.y))
                        self.dots[x].pop(0)  
        self.time += self.timeStep

    def load_planets(self) -> None:
        self.planets.clear()
        self.planets = self.saved_planets.copy()
        self.planet_count = len(self.planets)

    def save_planets(self) -> None:
        self.saved_planets = [planet.copy() for planet in self.planets]
        self.dots = [[(planet.x,planet.y)]*self.mem_size for planet in self.planets]

    def step_simulation(self) -> None:
        #assert not self.running, "Can only step simulation when not running"
        if self.running:
            self.log('Can only step simulation when not running')
            return
        self.update_simulation()
        self.draw_simulation()

    def collision_detected(self):
        for planet in self.planets:
            if planet.colliding(self.planets):
                return True
        return False

    def start_simulation(self) -> None:
        if self.collision_detected(): self.log('cannot start simulation with colliding objects'); return
        self.save_planets()
        self.running = True
        self.started = True

    def pause_simulation(self) -> None:
        if self.started:
            self.running = False
            self.active_state = self.state_paused

    def unpause_simulation(self) -> None:
        if self.started:
            self.running = True
            self.active_state = self.state_running
    
    def toggle_pause_simulation(self) -> None:
        if self.collision_type == 1 and self.collision_detected():
            self.log("Cannot unpause when objects are colliding")
            return
        if self.started:
            self.running = not self.running
            if self.running:
                self.active_state = self.state_running
            else:
                self.active_state = self.state_paused

    def end_simulation(self) -> None:
        self.running = False
        self.started = False
        self.active_state = self.state_stopped
        self.selected_body = Celestial_Body()

        self.load_planets()
        self.inspector.set_object(None)
        if hierarchy:
            hierarchy.dropdown.recalculate_options()
        #self.draw_simulation()

    def toggle_simulation(self) -> None:
        self.started = not self.started
        if not self.started:
            self.running = False
            self.active_state = self.state_stopped
            self.selected_body = Celestial_Body()
            self.load_planets()
            self.draw_simulation()              

            if hierarchy:
                hierarchy.dropdown.recalculate_options()
            self.log('')
            window_space.drawBorder('left')
        else: #just started running
            if self.collision_detected():
                self.log('Cannot start simulation with colliding objects.')
                self.started = False
                return
            self.save_planets()
            self.active_state = self.state_running
            for x,planet in enumerate(self.planets):
                self.dots[x] = [(planet.x,planet.y)]*self.mem_size
            self.running = True

    def set_accel_exaggeration(self,newVal) -> None:
        self.accel_exaggeration = int(newVal)

    def set_vel_exaggeration(self,newVal) -> None:
        self.vel_exaggeration = int(newVal)

    def add_Body(self,new_body:Celestial_Body):
        if self.planet_count == MAX_PLANETS:
            self.log('Maximum amount of planets placed')
            return
        if self.running:
            self.log('Cannot add new body while simulation is running.')
            return
        self.planets.append(new_body)
        self.dots.append([(new_body.x,new_body.y)]*self.mem_size)
        self.planet_count += 1
        if hierarchy:
            hierarchy.dropdown.recalculate_options()
        self.draw_simulation()

    def del_body(self,num:int) -> None:
        if self.planet_count == 1:
            self.log('At least one planet has to remain!')
            return
        if self.running:
            self.log('Cannot delete body while simulation is running.')
            return
        
        self.planets.pop(num)
        self.dots.pop(num)
        self.planet_count -= 1
        hierarchy.set_planet_count(self.planet_count)
        if hierarchy:
            hierarchy.dropdown.recalculate_options()
        self.draw_simulation()
  
    def draw_simulation(self):
        assert len(self.planets) == self.planet_count,'Error'
        surf = self.surf
        surf.fill((0,0,0))
        draw.line(surf,(80,80,80),(0,(self.simulation_camera_y - self.selected_body.y)/self.zoom+ self.size.y/2),(self.size.x,(self.simulation_camera_y - self.selected_body.y)/self.zoom + self.size.y/2))
        draw.line(surf,(80,80,80),((self.simulation_camera_x - self.selected_body.x)/self.zoom + self.size.x/2,0),((self.simulation_camera_x - self.selected_body.x)/self.zoom + self.size.x/2,self.size.y))
        if self.tracing:
            try:
                active_planet_num = self.planets.index(self.selected_body)
            except ValueError:
                active_planet_num = -1
            a = 0
            for dots in self.dots:
                if a != active_planet_num:
                    draw.lines(surf,(100,100,100),0,self.toSurfPoints(dots)) #[dot.toSurfPoint(self.selected_body.pos,self.zoom,self.simulation_camera_pos) for dot in dots]
                else:
                    draw.lines(surf,(255,215,10),0,self.toSurfPoints(dots))

                a += 1
        if self.show_vel and self.show_accel:
            for obj in self.planets:
                obj:Celestial_Body
                rad = obj.rad/self.zoom if obj.rad/self.zoom > 2 else 2
                x = (obj.x + self.simulation_camera_x - self.selected_body.x)/self.zoom + self.size.x/2
                y = (obj.y + self.simulation_camera_y - self.selected_body.y)/self.zoom + self.size.y/2
                if obj is not self.selected_body:
                    draw.circle(surf,obj.color,(x,y),rad,1)
                else:
                    draw.circle(surf,obj.color,(x,y),rad,3)
                ax = obj.ax * self.accel_exaggeration/self.zoom 
                ay = obj.ay * self.accel_exaggeration/self.zoom 
                vx = obj.vx * self.vel_exaggeration/self.zoom
                vy = obj.vy * self.vel_exaggeration/self.zoom
                py_line(surf,(100,0,100),(x,y),(x+ax,y+ay))
                py_line(surf,(0,100,0),(x,y),(x+vx,y+vy))
        elif self.show_accel:
            for obj in self.planets:
                obj:Celestial_Body
                rad = obj.rad/self.zoom if obj.rad/self.zoom > 2 else 2
                x = (obj.x + self.simulation_camera_x - self.selected_body.x)/self.zoom + self.size.x/2
                y = (obj.y + self.simulation_camera_y - self.selected_body.y)/self.zoom + self.size.y/2
                if obj is not self.selected_body:
                    draw.circle(surf,obj.color,(x,y),rad,1)
                else:
                    draw.circle(surf,obj.color,(x,y),rad,3)
                ax = obj.ax * self.accel_exaggeration/self.zoom
                ay = obj.ay * self.accel_exaggeration/self.zoom
                py_line(surf,(100,0,100),(x,y),(x+ax,y+ay))
        elif self.show_vel:
            for obj in self.planets:
                obj:Celestial_Body
                rad = obj.rad/self.zoom if obj.rad/self.zoom > 2 else 2
                x = (obj.x + self.simulation_camera_x - self.selected_body.x)/self.zoom + self.size.x/2
                y = (obj.y + self.simulation_camera_y - self.selected_body.y)/self.zoom + self.size.y/2
                if obj is not self.selected_body:
                    draw.circle(surf,obj.color,(x,y),rad,1)
                else:
                    draw.circle(surf,obj.color,(x,y),rad,3)
                vx = obj.vx * self.vel_exaggeration/self.zoom
                vy = obj.vy * self.vel_exaggeration/self.zoom
                py_line(surf,(0,100,0),(x,y),(x+vx,y+vy))
        else:
            for obj in self.planets:
                obj:Celestial_Body
                rad = obj.rad/self.zoom if obj.rad/self.zoom > 2 else 2
                if obj is not self.selected_body:
                    draw.circle(surf,obj.color,((obj.x + self.simulation_camera_x - self.selected_body.x)/self.zoom + self.size.x/2, (obj.y + self.simulation_camera_y - self.selected_body.y)/self.zoom + self.size.y/2),rad,1)
                else:
                    draw.circle(surf,obj.color,((obj.x + self.simulation_camera_x - self.selected_body.x)/self.zoom + self.size.x/2, (obj.y + self.simulation_camera_y - self.selected_body.y)/self.zoom + self.size.y/2),rad,3)
        
    @property
    def current_tool(self) -> int:
        return self._current_tool
    
    @current_tool.setter
    def current_tool(self,newVal) -> None:
        self._current_tool = newVal
        if newVal == self.tools.index('Move') or self.tools.index('Pan') == newVal:
            self.UnSelectBody()


    def select_Body(self,pos) -> Celestial_Body:
        assert isinstance(pos,(tuple,list)), 'pos arg must be tuple or list'
         

        for body in self.planets:
            dist = sqrt((pos[0]-body.x)**2 + (pos[1]-body.y)**2)
            if dist < body.rad:
                return body
        return None
    
    def check_clear(self,pos) -> bool:
        pos = Vector2(*pos)
        for body in self.planets:
            dist = sqrt((pos[0]-body.x)**2 + (pos[1]-body.y)**2)
            if dist < (body.rad + 10):
                return True
        return False

    def UnSelectBody(self) -> None:
        #copy the currentbodies pos
        current_body_x = self.selected_body.x
        current_body_y = self.selected_body.y
        #set selected body to new body with same pos
        self.selected_body = Celestial_Body((current_body_x,current_body_y))

    def pick_body(self,number:int) -> None:
        if self.planet_count <= number:
            if self.started:
                self.log('The planet picked seems to have been destroyed in the simulation')
            else:
                self.log('The planet picked no longer seems to exist, please restart application')
            return
        self.selected_body = self.planets[number]
        self.simulation_camera_x =  0
        self.simulation_camera_y =  0
        self.OnSelectBody(self.selected_body)
        inspector.set_object(self.selected_body)
        self.draw_simulation()

    def _OnSelectBody(self,body:Celestial_Body):
        pass
    def draw_circle(self,rad:float|int,pos:tuple,color = (255,255,255),width= 1):
        draw.circle(self.surf,color,pos,rad,width)

    def update(self,things):
        mpos, mb1down, mb1= things
        if self.running:
            for _x in range(self.simulation_speed):
                self.update_simulation()
            self.frames += 1
            if self._rect.collidepoint(mpos):
                if mb1down and self.current_tool == self.tools.index('Select'):
                    screen_x = (mpos[0] - self.pos.x - self._offSetPos[0] - self.size.x/2)*self.zoom - self.simulation_camera_x + self.selected_body.x
                    screen_y = (mpos[1] - self.pos.y - self._offSetPos[1] - self.size.y/2)*self.zoom - self.simulation_camera_y + self.selected_body.y
                    selected_body = self.select_Body((screen_x,screen_y))
                    if selected_body is not None:
                        self.OnSelectBody(selected_body)

                        self.selected_body = selected_body
                elif self.current_tool == self.tools.index('Pan') and mb1:
                    if mb1down:
                        self.prev_mpos = mpos
                    else:
                        self.simulation_camera_x += (mpos[0] - self.prev_mpos[0])*self.zoom
                        self.simulation_camera_y += (mpos[1] - self.prev_mpos[1])*self.zoom
                    
        elif self._rect.collidepoint(mpos):
            if mb1down and self.current_tool == self.tools.index('Select'):
                screen_x = (mpos[0] - self.pos.x - self._offSetPos[0] - self.size.x/2)*self.zoom - self.simulation_camera_x + self.selected_body.x
                screen_y = (mpos[1] - self.pos.y - self._offSetPos[1] - self.size.y/2)*self.zoom - self.simulation_camera_y + self.selected_body.y
                selected_body = self.select_Body((screen_x,screen_y))
                if selected_body is not None:
                    self.OnSelectBody(selected_body)
                    self.selected_body = selected_body
                    self.draw_simulation()
            elif self.current_tool == self.tools.index('Pan') and mb1:
                if mb1down:
                    self.prev_mpos = mpos
                self.simulation_camera_x += (mpos[0] - self.prev_mpos[0])*self.zoom
                self.simulation_camera_y += (mpos[1] - self.prev_mpos[1])*self.zoom
                self.draw_simulation()
            elif self.current_tool == self.tools.index('Move') and mb1:
                if mb1down:
                    screen_x = (mpos[0] - self.pos.x - self._offSetPos[0] - self.size.x/2)*self.zoom - self.simulation_camera_x + self.selected_body.x
                    screen_y = (mpos[1] - self.pos.y - self._offSetPos[1] - self.size.y/2)*self.zoom - self.simulation_camera_y + self.selected_body.y
                    body = self.select_Body((screen_x,screen_y))
                    if body is self.selected_body:
                        self.moving_body = None
                    else:
                        self.moving_body = body
                if self.moving_body:
                    self.moving_body.x = (mpos[0] - self.pos.x - self._offSetPos[0] - self.simulation_camera_x) * self.zoom
                    self.moving_body.y = (mpos[1] - self.pos.y - self._offSetPos[1] - self.simulation_camera_y) * self.zoom
                    self.draw_simulation()
                    self.inspector.set_object(self.moving_body)
            elif mb1down and self.current_tool == self.tools.index('Place Planet'):
                screen_x = (mpos[0] - self.pos.x - self._offSetPos[0] - self.size.x/2)*self.zoom - self.simulation_camera_x + self.selected_body.x
                screen_y = (mpos[1] - self.pos.y - self._offSetPos[1] - self.size.y/2)*self.zoom - self.simulation_camera_y + self.selected_body.y
                if self.check_clear((screen_x,screen_y)):
                    self.log('Adding a body there will overlap with a pre-existing body.')
                else:
                    self.add_Body(Celestial_Body((screen_x,screen_y),rad = 10,name = f'Planet #{len(self.planets)}',color = hsv_to_rgb(random(),1,1)))
                    hierarchy.set_planet_count(self.planet_count)
                    window_space.drawBorder('left')
        else:
            self.moving_body = None
        self.prev_mpos = mpos
            
    def draw(self):
        if self.running:
            self.draw_simulation()
        framework.screen.blit(self.surf,self.screen_pos)
        framework.screen.blit(self.active_state,self.screen_pos)

class Vector_Dragger:
    @classmethod
    def accepts(cls) -> tuple:
        return ('mpos','mb1')
    
    def __init__(self,pos,size,output):
        self.pos = pos
        self.size = size
        self.posVec = Vector2(*pos)
        self.sizeVec = Vector2(*size)
        self._rect = Rect(pos,size)
        self.midpoint = (Vector2(*pos) + Vector2(*size)/2).to_tuple
        self.vecPoint = Vector2(50,0)
        self.output = output

    @property
    def offSetPos(self) -> tuple:
        raise SyntaxError('use instead ._offSetPos')

    @offSetPos.setter
    def offSetPos(self,newVal) -> None:
        self._offSetPos = newVal
        vec = Vector2(*newVal)
        self.midpoint = (vec + self.posVec + self.sizeVec/2).to_tuple
        self._rect = Rect((vec+self.posVec).to_tuple,self.size)

    def update(self,things):
        'mpos,mb1'
        mpos,mb1= things
        if mb1 and self._rect.collidepoint(mpos):
            mpos = Vector2(*mpos)
            self.vecPoint = mpos-Vector2(*self.midpoint)
            self.output(self.vecPoint)

    def draw(self):
        draw.rect(framework.screen,(30,30,30),self._rect)
        draw.line(framework.screen,(0,150,0),self.midpoint,(self.vecPoint+Vector2(*self.midpoint)).to_tuple,3)
        draw.circle(framework.screen,(255,0,0),self.midpoint,5)
        draw.circle(framework.screen,(0,150,0),(self.vecPoint+Vector2(*self.midpoint)).to_tuple,5)

class Settings_Panel:
    @classmethod
    def accepts(cls) -> tuple:
        return ('mpos','mb1down','mb1up','KDQueue')

    def __new__(cls): #makes this class a singleton object , meaning that this class is restricted to one instance during runtime.
        if not hasattr(cls, 'instance'):
            cls.instance = super(Settings_Panel, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        font = makeFont('Arial',18)
        self.G_title = TextBox((10,25),font,'Gravitational Constant',black)
        self.G_setter = InputBox((10,47),(500,18),'G=',light_grey,23,self.set_G,numbers.union({back_unicode,'e'}),14)
        self.trail_size_title = TextBox((10,70),font,'Trail Size: ',black)
        self.trail_size_setter = Slider(10,95,500,8,50,500,self.set_mem_size,light_dark_grey,light_grey,starting_value = 100)
        self.trail_hertz_title = TextBox((10,107),font,'Frames Per Sample',black)
        self.trail_hertz_setter = Slider(10,132,500,8,2,120,self.set_trace_impact,light_dark_grey,light_grey,starting_value=30)
        self.sim_speed_title = TextBox((10,145),font,'Simulation Speed: ',black)
        self.sim_speed_setter = DesmosSlider((10,165),(500,20),1,10,self.set_sim_speed,light_dark_grey,light_grey,starting_value=1)
        self.accel_exaggeration_title = TextBox((10,185),font,'Acceleration Exaggeration: ',black)
        self.accel_exaggeration_setter = DesmosSlider((10,206),(500,20),100_000,500_001,self.set_accel_exag,light_dark_grey,light_grey,500_000,6)
        self.vel_exaggeration_title = TextBox((10,225),font,'Velocity Exaggeration: ',black)
        self.vel_exaggeration_setter = DesmosSlider((10,246),(500,20),500,5001,self.set_vel_exag,light_dark_grey,light_grey,1_000,4)
        self.friction_title = TextBox((10,265),font,'Friction : 1%',black)
        self.friction_setter = Slider(10,290,500,8,0,102,self.set_friction,light_dark_grey,light_grey,starting_value= 1)
        self.timeStep_title = TextBox((10,305),font,'Time Step: 1',black)
        self.timeStep_setter = DesmosSlider((10,330),(500,20),1,10,self.set_timeStep,light_dark_grey,light_grey,1)
        self.done_Button = Button((10,395),100,20,self.close_settings,light_green,light_green,green,'Done',30,-1)
        self.G_setter.set_text(str(G))
        self.friction_setter.set_value(50)
        self.trail_hertz_setter.set_value(scene.trace_impact)
        self.sim_speed_setter.set_value(scene.simulation_speed)
        self.trail_size_setter.set_value(scene.mem_size)
        self.trail_size_title.set_text(f'Trail Size: {scene.mem_size}')
        self.trail_hertz_title.set_text(f'Frames Per Sample: {scene.trace_impact:,}')
        self.accel_exaggeration_title.set_text(f'Acceleration Exaggeration: {scene.accel_exaggeration:,}')
        self.vel_exaggeration_title.set_text(f'Velocity Exaggeration: {scene.vel_exaggeration:,}')
        self.sim_speed_title.set_text(f'Simulation Speed: {scene.simulation_speed:,}')
        
        self.mpos:Vector2

    def set_timeStep(self,newVal):
        scene.timeStep = int(newVal)
        self.timeStep_title.setText(f'Time Step: {scene.timeStep}')

    def set_sim_speed(self,newVal):
        scene.set_sim_speed(int(newVal))
        self.sim_speed_title.set_text(f'Simulation Speed: {scene.simulation_speed:,}')

    def set_accel_exag(self,newVal):
        scene.set_accel_exaggeration(int(newVal))
        self.accel_exaggeration_title.set_text(f'Acceleration Exaggeration: {scene.accel_exaggeration:,}')

    def set_vel_exag(self,newVal):
        scene.set_vel_exaggeration(int(newVal))
        self.vel_exaggeration_title.set_text(f'Velocity Exaggeration: {scene.vel_exaggeration:,}')
    
    def set_friction(self,newVal):
        global Friction
        Friction = 1-newVal/1000 
        if Friction > 1:
            Friction = 1
        elif Friction < 0:
            Friction = 0
        self.friction_title.set_text(f'Friction: {int((1-Friction)*1000)/10}%')

    def close_settings(self) -> None:
        scene.prev_mpos = Vector2(*self.mpos)
        window_space.deactivateMiniWindow()

    def set_trace_impact(self,newVal) -> None:
        scene.set_trace_impact(newVal)
        self.trail_hertz_title.set_text(f'Frames Per Sample: {scene.trace_impact}')

    def set_mem_size(self,newVal) -> None:
        scene.set_mem_size(newVal)
        self.trail_size_title.set_text(f'Trail Size: {scene.mem_size}')

    def set_G(self,newVal):
        global G
        try:
            G = float(newVal)
        except ValueError :
            G = 1e-5
    @property
    def offSetPos(self) -> tuple:
        raise SyntaxError("Use ._offSetPos")
    
    @offSetPos.setter
    def offSetPos(self,newVal) -> None:
        self.G_title.offSetPos = newVal
        self.G_setter.offSetPos = newVal
        self.trail_size_title.offSetPos = newVal
        self.trail_size_setter.offSetPos = newVal
        self.trail_hertz_title.offSetPos = newVal
        self.trail_hertz_setter.offSetPos = newVal
        self.sim_speed_title.offSetPos = newVal
        self.sim_speed_setter.offSetPos = newVal
        self.done_Button.offSetPos = newVal
        self.accel_exaggeration_title.offSetPos = newVal
        self.accel_exaggeration_setter.offSetPos = newVal
        self.vel_exaggeration_title .offSetPos = newVal
        self.vel_exaggeration_setter.offSetPos = newVal
        self.friction_title.offSetPos = newVal
        self.friction_setter.offSetPos = newVal
        self.timeStep_title.offSetPos = newVal
        self.timeStep_setter.offSetPos = newVal

    def update(self,things):
        mpos,mb1down,mb1up,KDQueue = things
        self.mpos = mpos
        self.trail_hertz_setter.update((mpos,mb1down,mb1up))
        self.trail_size_setter.update((mpos,mb1down,mb1up))
        
        self.G_setter.update((mpos,mb1down,KDQueue))
        self.sim_speed_setter.update(things)
        self.done_Button.update((mpos,mb1down,0,KDQueue,mb1up))
        self.accel_exaggeration_setter.update(things)
        self.vel_exaggeration_setter.update(things)
        self.friction_setter.update((mpos,mb1down,mb1up))
        self.timeStep_setter.update(things)

    def draw(self):
        self.G_title.draw()
        self.G_setter.draw()
        self.trail_size_title.draw()
        self.trail_size_setter.draw()
        self.trail_hertz_title.draw()
        self.trail_hertz_setter.draw()
        self.sim_speed_title.draw()
        self.sim_speed_setter.draw()
        self.done_Button.draw()
        self.accel_exaggeration_title.draw()
        self.accel_exaggeration_setter.draw()
        self.vel_exaggeration_title .draw()
        self.vel_exaggeration_setter.draw()
        self.friction_title.draw()
        self.friction_setter.draw()
        self.timeStep_title.draw()
        self.timeStep_setter.draw()
        
class Side_Panel:
    @classmethod
    def accepts(cls) -> tuple:
        return ('mpos','mb1down','mb1up')
    
    def __init__(self,pos,func):
        self.pos = pos
        self.vec_x = TextBox((pos[0]+5,pos[1]+20),makeFont('Arial',12),'NaN',(0,0,0))
        self.vec_y = TextBox((pos[0]+5,pos[1]+43),makeFont('Arial',12),'Nan',(0,0,0))
        self.done = Button((pos[0]+5,pos[1]+70),100,21,self.be_done,dark_light_grey,dark_light_grey,light_dark_grey,'Done',25)
        self.slider = Slider(pos[0]+120, pos[1]+70,130,6,0,1000,self.set_mag,light_grey,blue)
        self.vector = Vector2(0)
        self.slider.set_value(100)
        self.magnitude = (1/100000)
        self.func = func

    def be_done(self):
        self.func(self.vector*self.magnitude)
        window_space.deactivateMiniWindow()


    def set_mag(self,newVal) -> None:
        self.magnitude = (newVal/100000)
        self.vec_x.setText('X: '+str(self.vector.x*self.magnitude))
        self.vec_y.setText('Y: '+str(self.vector.y*self.magnitude))

    @property
    def offSetPos(self):
        return self._offSetPos

    @offSetPos.setter
    def offSetPos(self,newVal) -> None:
        self._offSetPos = newVal
        self.vec_x.offSetPos = newVal
        self.vec_y.offSetPos = newVal
        self.done.offSetPos = newVal
        self.slider.offSetPos = newVal
    
    def set_vector(self,newVector:Vector2) -> None:
        self.vector = newVector
        self.vec_x.setText('X: '+str(self.vector.x*self.magnitude))
        self.vec_y.setText('Y: '+str(self.vector.y*self.magnitude))

    def update(self,things):
        'mpos,mb1down,mb1up'
        mpos, mb1down, mb1up = things
        self.done.update((mpos,mb1down,0,[],mb1up))
        self.slider.update(things)

    def draw(self):
        self.vec_x.draw()
        self.vec_y.draw()
        self.done.draw()
        self.slider.draw()

scene = Editor_Window((0,0),(0,0))
hierarchy = Hierarchy.__new__(Hierarchy,)
inspector = Inspector((0,0),0)

def get_all_saves() -> list[str]:
    return [file for file in findAllFiles('.json','Saves')]

def check_if_to_override(fileName):
    return (fileName in get_all_saves())

def save_file(fileName): 
    with open('Saves/'+fileName+'.json','wb') as file:
        file.write(scene.get_settings().encode('utf-8'))

save_file('ErfAndSun')
