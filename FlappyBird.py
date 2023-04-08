import pygame
import os
import random

screen_width = 500
screen_height = 800

pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
floor_img = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
background_img = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
bird_img = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
]

pygame.font.init()
hud = pygame.font.SysFont('arial', 50)

class Bird:
    imgs = bird_img
    rotation_max = 25
    speed_max = 20
    time_animation = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = -10
        self.speed = 0
        self.height = self.y
        self.time = 0
        self.count_img = 0
        self.img = self.imgs[0]

    def jump(self):
        self.speed = -10.5
        self.time = 0
        self.height = self.y

    def move(self):
        #DESLOCAMENTO
        self.time += 1
        displace = 1.8 * (self.time**2) + self.speed * self.time

        #BLOQUEIO
        if displace > 16:
            displace = 16
        elif displace < 0:
            displace -= 2

        self.y += displace

        #ÂNGULO
        if displace < 0 or self.y < (self.height + 50):
            if self.angle < self.rotation_max:
                self.angle = self.rotation_max
            else:
                if self.angle > -90:
                    self.angle -= self.speed_max

    def draw(self, frame):
        #Definição da animação
        self.count_img += 1
        if self.count_img < self.time_animation:
            self.img = self.imgs[0]
        elif self.count_img < self.time_animation*2:
            self.img = self.imgs[1]
        elif self.count_img < self.time_animation*3:
            self.img = self.imgs[2]  
        elif self.count_img < self.time_animation*4:
            self.img = self.imgs [1]
        elif self.count_img < self.time_animation*4 + 1:
            self.img = self.imgs[0]
            self.count_img = 0

        if self.angle <= -80:
            self.img = self.imgs[1]
            self.count_img = self.time_animation*2

        rotade_img = pygame.transform.rotate(self.img, self.angle)
        pos_img_center = self.img.get_rect(topleft = (self.x, self.y)).center
        screen = rotade_img.get_rect(center = pos_img_center)
        frame.blit(rotade_img, screen.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    distance = 200
    speed = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.pipetop = pygame.transform.flip(pipe_img, False, True)
        self.pipebottom = pipe_img
        self.spend = False
        self.define_height()

    def define_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.pipetop.get_height()
        self.bottom = self.height + self.distance

    def move(self):
        self.x -= self.speed
    
    def draw(self, frame):
        frame.blit(self.pipetop, (self.x, self.top))
        frame.blit(self.pipebottom, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()

        top_mask = pygame.mask.from_surface(self.pipetop)
        bottom_mask = pygame.mask.from_surface(self.pipebottom)

        distance_top = (self.x - bird.x, self.top - round(bird.y))
        distance_bottom = (self.x - bird.x, self.bottom - round(bird.y))

        top_point = bird_mask.overlap(top_mask, distance_bottom)
        bottom_point = bird_mask.overlap(bottom_mask, distance_top)

        if bottom_point or top_point:
            return True
        else:
            return False

class Floor:
    speed = 5
    width = background_img.get_width()
    img = floor_img

    def __init__(self, y):
        self.y = y
        self.x0 = 0
        self.x1 = self.width

    def move(self):
        self.x0 -= self.speed
        self.x1 -= self.speed

        if self.x0 + self.width < 0:
            self.x0 = self.x1 + self.width
        if self.x1 + self.width < 0:
            self.x1 = self.x0 + self.width

    def draw(self, frame):
        frame.blit(self.img, (self.x0, self.y))
        frame.blit(self.img, (self.x1, self.y))

def draw_frame(frame, birds, pipes, floor, score):
    frame.blit(background_img, (0, 0))
    for bird in birds:
        bird.draw(frame)
    for pipe in pipes:
        pipe.draw(frame)

    text = hud.render(f"Portuação: {score}", 1, (255, 255, 255))
    frame.blit(text, (screen_width - 10 - text.get_width(), 10))
    floor.draw(frame)
    pygame.display.update()

def main():
    birds = [Bird(230, 350)]
    floor = Floor(730)
    pipes = [Pipe(700)]
    frame = pygame.display.set_mode((screen_width, screen_height))
    score = 0
    clock = pygame.time.Clock()

    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.type == pygame.MOUSEBUTTONDOWN:
                    for bird in birds:
                        bird.jump()
        
        for bird in birds:
            bird.move()
        floor.move()

        add_pipe = False
        remove_pipe = []

        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.collide(bird):
                    birds.pop(i)
                if not pipe.spend and bird.x > pipe.x:
                    pipe.spend = True
                    add_pipe = True
            pipe.move()

            if pipe.x + pipe.pipetop.get_width() < 0:
                remove_pipe.append(pipe)

        if add_pipe:
            score += 1
            pipes.append(Pipe(600))
        
        for pipe in remove_pipe:
            pipes.remove(pipe)

        for i, bird in enumerate(birds):
            if (bird.y + bird.img.get_height()) > floor.y or bird.y < 0:
                birds.pop(i)

        draw_frame(frame, birds, pipes, floor, score)

if __name__ == '__main__':
    main()