import intersect
import pygame
import math
from pygame.math import Vector2
import random
import threading
import time

class Doodle:
    
    jumpVal = -10
    def __init__(self):
        self.pos = Vector2(50, 100)
        self.size = (45, 45)
        self.image = pygame.image.load('doodle.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, self.size)
        self.speed = Vector2(0, 0)
        
    def jump(self):
        self.speed.y = Doodle.jumpVal
        
    def move(self, length = None):

        if length is None:
            self.pos += self.speed
        elif length != 0 and self.speed.length() != 0:
            self.pos += self.speed.normalize() * length
            
        self.speed.y += 0.4

        if self.pos.x > size[0] or self.pos.x < 0:
            self.speed = Vector2(-self.speed.x, Doodle.jumpVal)

        global offset
        if self.pos.y + offset < 50:
            append_offset(50 - self.pos.y - offset)

    def draw(self):
        global offset
        screen.blit(self.image, (self.pos.x, self.pos.y + offset))


class Platform:
    
    def __init__(self, x, y):
        self.create(x, y)
        
    def create(self, x, y):
        self.pos = Vector2(x, y)
        self.size = (100, 20)
        self.color = (0, 255, 0)
        self.is_alive = True

    def draw(self):
        global offset
        pygame.draw.rect(screen, self.color,
                       ((self.pos.x, self.pos.y + offset), self.size))

    def touch(self):
        pass


class WeakPlatform(Platform):
    def __init__(self, x, y):
        self.create(x, y)
        self.color = (50, 50, 0)
    
    def touch(self):
        self.is_alive = False


class Bonus:
    
    def __init__(self, x, y):
        self.pos = Vector2(x, y)
        self.size = (10, 10)
        self.is_alive = True
        
    def draw (self):
        pygame.draw.rect(screen, (255,255,0), ((self.pos.x, self.pos.y + offset), self.size))
    
    def take (self, doodle):

        counter = 5
        def add_speed():
            nonlocal counter
            doodle.speed.y = -15
            counter -= 1
            if counter <= 0:
                return
            threading.Timer(0.2, add_speed).start()
        
        add_speed()
        self.is_alive = False
        global score
        score += 1


class Container:
    
    def __init__(self, classes):
        self.classes = classes
        self.objects = []
        self.locker = threading.Lock()
        
    def generate(self, count):
        new_objects = []
        for i in range(count):
            obj = self.classes[random.randint(0, len(self.classes)-1)]
            obj = obj(random.randint(20, 500), 80 * i - offset)
            new_objects.append(obj)
            
        self.locker.acquire()
        self.objects += new_objects
        self.locker.release()
        
    def clear_not_alive(self):
        i = 0
        self.locker.acquire()
        while i < len(self.objects):
            if not self.objects[i].is_alive:
                del self.objects[i]
            else:
                i += 1
        self.locker.release()
    
    def draw(self):
        self.locker.acquire()
        objects = list(self.objects)
        self.locker.release()
        
        for o in objects:
            o.draw()
    
    def check_under_screen(self):
        self.locker.acquire()
        objects = list(self.objects)
        self.locker.release()
        
        i = 0
        while i < len(objects):
            o = objects[i]
            if o.pos.y + offset > 800:
                del objects[i]
            else:
                i += 1
        
        self.locker.acquire()
        self.objects = objects
        self.locker.release()
    
    def __len__(self):
        return len(self.objects)
        

def intersects(platform, doodle, speed):
        lt = (platform.pos.x, platform.pos.y) # left top
        lb = (platform.pos.x, platform.pos.y + platform.size[1]) # left bottom
        rt = (platform.pos.x + platform.size[0], platform.pos.y) # right top
        rb = (platform.pos.x + platform.size[0], platform.pos.y + platform.size[1]) # right bottom

        points = ((doodle.pos.x, doodle.pos.y),
                  (doodle.pos.x + doodle.size[0], doodle.pos.y),
                  (doodle.pos.x, doodle.pos.y + doodle.size[1]),
                  (doodle.pos.x + doodle.size[0], doodle.pos.y + doodle.size[1]))

        min_dist = None
        for start in points:
            end = (start[0] + speed.x, start[1] + speed.y)

            top_intersect = intersect.calculateIntersectPoint(start, end, lt, rt)
            left_intersect = intersect.calculateIntersectPoint(start, end, lt, lb)
            right_intersect = intersect.calculateIntersectPoint(start, end, rt, rb)
            bottom_intersect = intersect.calculateIntersectPoint(start, end, lb, rb)

            if top_intersect is not None:
                length = intersect.distance(start, top_intersect)
                if min_dist is None or length < min_dist[1]:
                    min_dist = ('top', length)
            if left_intersect is not None:
                length = intersect.distance(start, left_intersect)
                if min_dist is None or length < min_dist[1]:
                    min_dist = ('left', length)
            if right_intersect is not None:
                length = intersect.distance(start, right_intersect)
                if min_dist is None or length < min_dist[1]:
                    min_dist = ('right', length)
            if bottom_intersect is not None:
                length = intersect.distance(start, bottom_intersect)
                if min_dist is None or length < min_dist[1]:
                    min_dist = ('bottom', length)

        return min_dist

def append_offset(count):
    global offset
    offset += count
    if random.randint(0, 7) == 0:
        platforms.generate(1)
    if random.randint(0, 30) == 0:
        bonuses.generate(1)


class GameThread (threading.Thread):
    threads = []
    working = True
    delay = 0.005
    def __init__(self, run):
        threading.Thread.__init__(self)
        self.running = True
        self.cycle_func = run
        GameThread.threads.append(self)

    def stop_all():
        GameThread.working = False
        for t in GameThread.threads:
            if threading.currentThread() != t:
                t.join()

    def join_all():
        for t in GameThread.threads:
            t.join()

    def stop(self):
        self.running = False

    def run(self):
        while GameThread.working and self.running:
            self.cycle_func()
            time.sleep(GameThread.delay)


class KeyEvents:
    def __init__(self):
        self.__locker = threading.Lock()
        self.__events = []
    
    def get(self):
        self.__locker.acquire()
        l = self.__events
        self.__events = []
        self.__locker.release()
        return l
    
    def add(self, events):
        self.__locker.acquire()
        self.__events += events
        self.__locker.release()
    
    def __len__(self):
        return len(self.__events)

# Pygame initialization
pygame.init()
size = [600, 800]
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
myfont = pygame.font.SysFont("arial", 15)
events = KeyEvents()

# System initialization
screen_text = ""
pause = False
jumpClock = -5000

# Game initialization
score = 0
offset = 0
doodle = Doodle()
doodle.jump()
platforms = Container([Platform, WeakPlatform])
platforms.generate(15)
bonuses = Container([Bonus])
bonuses.generate(2)

def logic_cycle():
    global pause
    global jumpClock
    global events
    
    # Check for input
    for event in events.get():
        if event.type == pygame.QUIT:
            GameThread.stop_all()
            
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                pause = not pause
            if pause: continue
            
            if event.key == pygame.K_UP:
                if pygame.time.get_ticks() - jumpClock > 2500:
                    doodle.jump()
                    jumpClock = pygame.time.get_ticks()
                    
            if event.key == pygame.K_LEFT:
                doodle.speed.x = -5
                
            elif event.key == pygame.K_RIGHT:
                doodle.speed.x = 5
    
    # Moving objects, resolving intersections
    if not pause:

        bonuses.check_under_screen()
        for bonus in bonuses.objects:
            if intersects(doodle, bonus, doodle.speed) or intersects(bonus, doodle, doodle.speed):
                bonus.take(doodle)
        bonuses.clear_not_alive()
        
        min_dist = None
        platforms.check_under_screen()
        for platform in platforms.objects:
            distance = intersects(platform, doodle, doodle.speed)
            if distance is not None:
                if distance[0] == 'top' and doodle.speed.y > 0:
                    if min_dist is None or min_dist[1] > distance[1]:
                        min_dist = distance
                    platform.touch()
     
                elif distance[0] == 'left' or distance[0] == 'right':
                    doodle.speed.x = 0
        platforms.clear_not_alive()
        
        if min_dist is not None:
            doodle.speed = Vector2()
            doodle.move(min_dist[1] * 0.9)
            if min_dist[0] == 'top':
                doodle.jump()
        else:
            doodle.move()

        if doodle.pos.y > 800 - offset:
            GameThread.stop_all()
            
        
def drawing_cycle():
    global text
    # Drawing level
    screen.fill((120, 210, 120))
    
    doodle.draw()
    bonuses.draw()
    platforms.draw()
    
    screen_text = "Score: " + str(score)
    label = myfont.render(screen_text, 1, (255,255,255))
    screen.blit(label, (10, 10))
    pygame.display.flip()
    #input()
    clock.tick(0)

logic_thread = GameThread(logic_cycle)
draw_thread = GameThread(drawing_cycle)

logic_thread.start()
draw_thread.start()
while GameThread.working:
    new_events = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            GameThread.stop_all()
        
        if event.type == pygame.KEYDOWN:
            new_events.append(event)
    
    events.add(new_events)

GameThread.join_all()

print ("Score: " + str(score))
pygame.quit()
