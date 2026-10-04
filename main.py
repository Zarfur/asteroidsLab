import random
import math
import pygame

WIDTH = 900
LEN = 600

pygame.init()
screen = pygame.display.set_mode((WIDTH, LEN))
pygame.display.set_caption("Asteroid Game")
clock = pygame.time.Clock()
THRUST = 0.15
DRAG = 0.99
MAX_SPEED = 6

asteroid_image = pygame.image.load("Verity.png").convert_alpha()


asteroid_image = pygame.transform.scale(asteroid_image,(50, 50))

class Asteroid:

    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, LEN)
        self.dx = random.randint(-2, 2)
        self.dy = random.randint(-2, 2)
        self.radius = random.randint(10, 15)
        self.position = pygame.math.Vector2(self.x, self.y)
        self.velocity = pygame.math.Vector2(self.dx, self.dy)
        self.image = pygame.transform.scale(asteroid_image,( self.radius,  self.radius))
   
    def move(self):
        self.position += self.velocity
        self.moveToOtherSide()


    def moveToOtherSide(self):
        if self.position.x > WIDTH:
            self.position.x = 0

        if self.position.x < 0:
            self.position.x= WIDTH

        if self.position.y > LEN:
            self.position.y  = 0

        if self.position.y  < 0:
            self.position.y = LEN
   
    def draw(self):
            screen.blit(self.image, self.position)


    def checkCollision(self, other):
        difference = other.position - self.position
        distance = difference.length()
        if distance >= self.radius + other.radius or distance == 0:
            return

        normalized = difference.normalize()

        # taken from interweb
        relative_velocity = self.velocity - other.velocity
        velocity_among_normal = relative_velocity.dot(normalized)

        overlap = (self.radius + other.radius) - distance

        self.position -= normalized * overlap/2
        other.position += normalized * overlap/2

        if velocity_among_normal < 0: 
            return

        self.velocity -= velocity_among_normal * normalized
        other.velocity += velocity_among_normal * normalized        

    def destroy(self):
        global asteroids
        if self in asteroids:
            asteroids.remove(self)

class Player:
    def __init__(self):
        self.hp = 200
        self.position = pygame.math.Vector2(WIDTH/2,LEN/2)
        self.missile_speed = 7
        self.angle = 90
        self.radians = 0
        self.radius = 10
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0,0)
        self.forward = pygame.math.Vector2(math.cos(self.radians), -math.sin(self.radians))

    def shoot(self):
        global missiles

        missile_velocity = self.forward.normalize() * self.missile_speed

        missiles.append(Missile(self.position, missile_velocity, "white"))
        return

    def draw(self):
        left = self.forward.rotate(140)
        right = self.forward.rotate(-140)
        p1 = self.position + self.forward * 11
        p2 = self.position + left * 8
        p3 = self.position + right * 8

        pygame.draw.polygon(screen, "white", [p1, p2, p3],2)

    def move(self, keys):
        self.force = 0
        self.acceleration = self.forward * THRUST
        
        self.radians = math.radians(self.angle)
        self.forward = pygame.math.Vector2(math.cos(self.radians), -math.sin(self.radians))
        if keys[pygame.K_LEFT]:
            self.angle += 6
        if keys[pygame.K_RIGHT]:
            self.angle -= 6
        if keys[pygame.K_UP]:
            self.velocity += self.acceleration
        
        if self.velocity.length() > MAX_SPEED:
            self.velocity.scale_to_length(MAX_SPEED)
        
        self.position += self.velocity
        self.velocity *= DRAG
     
        self.moveToOtherSide()

    def moveToOtherSide(self):
        if self.position.x > WIDTH:
            self.position.x = 0

        if self.position.x < 0:
            self.position.x= WIDTH

        if self.position.y > LEN:
            self.position.y  = 0

        if self.position.y  < 0:
            self.position.y = LEN
    def destroy(self):
        reset_game()


class Enemy:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, LEN)
        self.dx = random.randint(-2, 2)
        self.dy = random.randint(-2, 2)
        self.missile_speed = 4
        self.radians = 0
        self.position = pygame.math.Vector2(self.x, self.y)
        self.velocity = pygame.math.Vector2(self.dx, self.dy)
        self.acceleration = pygame.math.Vector2(0,0)
        self.forward = pygame.math.Vector2(math.cos(self.radians), -math.sin(self.radians))
        self.state = "patrol"
        self.detection_radius = 150
        self.FOV = 0.3
        self.target = None
        self.radius = 10

    def draw(self):
        left = self.forward.rotate(140)
        right = self.forward.rotate(-140)
        p1 = self.position + self.forward * 11
        p2 = self.position + left * 8
        p3 = self.position + right * 8

        pygame.draw.polygon(screen, "red", [p1, p2, p3],2)

    def check_state(self, player):
        self.target = player
        distance = (player.position - self.position).length()

        if distance < 10:                      
            self.state = "kill"
        elif distance < self.detection_radius and self.forward.dot((player.position - self.position).normalize()) > self.FOV:
                self.state = "pursuit"
        else:
            self.state = "patrol"

    def update(self):

        if self.state == "kill":
            reset_game()

        if self.state == "patrol":
            if random.randint(0, 25) <= 1:
                self.dx = random.randint(-2, 2)
                self.dy = random.randint(-2, 2)
            self.velocity += pygame.math.Vector2(self.dx, self.dy) * 0.25
            if random.randint(0, 100) <= 1:
                self.shoot()

        elif self.state == "pursuit":
            if random.randint(0, 60) <= 1:
                self.shoot()
            to_target = self.target.position - self.position
            if to_target.length() > 0:
                self.velocity += to_target.normalize() * 0.5

        if self.velocity.length() > MAX_SPEED:
            self.velocity.scale_to_length(MAX_SPEED)

        self.velocity *= DRAG
        self.position += self.velocity

        if self.velocity.length() > 0.1:
            self.forward = self.velocity.normalize()

        self.moveToOtherSide()

    def moveToOtherSide(self):
        if self.position.x > WIDTH:
            self.position.x = 0

        if self.position.x < 0:
            self.position.x= WIDTH

        if self.position.y > LEN:
            self.position.y  = 0

        if self.position.y  < 0:
            self.position.y = LEN

    def destroy(self):
        global enemies
        if self in enemies:
            enemies.remove(self)
    
    def shoot(self):
        global enemyMissiles

        missile_velocity = self.forward.normalize() * self.missile_speed

        enemyMissiles.append(Missile(self.position, missile_velocity, "red"))

            
    
        

class Missile:

    def __init__(self, origin, velocity, color):
        self.position = pygame.math.Vector2(origin)
        self.velocity = velocity
        self.radius = 4
        self.color = color

    def draw(self):
        pygame.draw.circle(screen, self.color, self.position, self.radius)

    def move(self):
        self.position += self.velocity

    def destroy(self):
        global missiles
        if self in missiles:
            missiles.remove(self)

    def collide(self, other):
        difference = other.position - self.position
        distance = difference.length()
        if distance >= self.radius + other.radius or distance == 0:
            return
    
        other.destroy()
        self.destroy()


    
def draw_stuff():
    
    player.draw()

    for asteroid in asteroids:
        asteroid.draw()
    
    for missile in missiles + enemyMissiles:
        missile.draw()

    for enemy in enemies:
        enemy.draw()

def update():

    if len(enemies) ==0:
        reset_game()
    for asteroid in asteroids:
        asteroid.move()

    for missile in missiles + enemyMissiles:
        missile.move()

    for missile in enemyMissiles[:]:
        missile.collide(player)

    for enemy in enemies[:]:         
        enemy.check_state(player)
        enemy.update()

    for i in range(len(asteroids)):
        for j in range(i + 1, len(asteroids)):
            asteroids[i].checkCollision(asteroids[j])

def reset_game():
    global player, asteroids, missiles, enemies

    player = Player()
    asteroids = []
    missiles = []
    enemies = []

    for i in range(35):
        asteroids.append(Asteroid())

    for i in range(3):
        enemies.append(Enemy())

player = Player()

asteroids = []
missiles = []
enemyMissiles = []
enemies = []

running = True
timer = 0

for i in range(35):
    asteroids.append(Asteroid())


for i in range(2):
    enemies.append(Enemy())



while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((20, 24, 40))
    timer += 1

    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        if timer >= 10:
            timer = 0
            player.shoot()
    if keys[pygame.K_v]:
        enemies.append(Enemy())

    for asteroid in asteroids:
        for missile in missiles + enemyMissiles:
            missile.collide(asteroid)

    for enemy in enemies:
        for missile in missiles:
            missile.collide(enemy)
        
    draw_stuff()
    player.move(keys)
    update()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
