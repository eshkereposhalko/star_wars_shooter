import pygame
import random

pygame.init()
RED = (255, 0 , 0)
BLUE = (0, 0 , 255)
WIDTH = 1920 - 50
HEIGHT = 1080 - 100
BLACK = (0, 0 ,0)
TICKRATE = 60
WHITE = (255, 255, 255)


window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Space Wars')


clock = pygame.time.Clock()



class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, callback = None):
        super().__init__()
        self.callback = callback
        self.frames_count = 12
        self.current_frame = 0
        self.frame_cd = Cooldown(TICKRATE // 10)
        image = pygame.image.load('Explosion.png')
        frame_width = image.get_width() // self.frames_count
        frame_height = image.get_height()
        self.rect = (x - frame_width // 2, y - frame_height // 2)
        self.frames = []
        for i in range(self.frames_count):
            self.frames.append(image.subsurface(i * frame_width, 0 , frame_width, frame_height))
            self.image = self.frames[0]
    def update(self):
        if self.frame_cd.done():
            self.current_frame += 1
            if self.current_frame == self.frames_count:
                self.kill()
                if self.callback:
                    self.callback()
            else:
                self.image = self.frames[self.current_frame]

class Cooldown():
    def __init__(self, ticks):
        self.ticks = ticks
        self.current = ticks


    def reset(self):
        self.current = self.ticks


    def done(self , need_reset = True):
        if self.current == 0:
            if need_reset:
                self.reset()
            return True
        else:
            self.current -= 1
            return False

class Text():
    def __init__(self, text, size, x, y):
        self.font = pygame.font.Font('pixel.ttf' , size)
        self.text = self.font.render(text, True, WHITE)
        self.rect = self.text.get_rect(center=(x, y))

    def draw(self):
        window.blit(self.text, self.rect)

    def update(self, text):
        self.text = self.font.render(text, True, WHITE)

class SpaceShip(pygame.sprite.Sprite ):
    def __init__(self, image, x, y,speed, shoot_cd = TICKRATE, hp = 1):
        super().__init__()
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.shoot_cd = Cooldown(shoot_cd)
        self.hp = hp
        self.max_hp = hp


    def draw(self):
        window.blit(self.image, self.rect)


class Player(SpaceShip):
    def __init__(self):
        super().__init__(image='sith-ship.png',
        x = WIDTH // 2,
        y = HEIGHT // 2,
        speed = 20,
        shoot_cd = TICKRATE // 5,
        hp = 5
        )
    def draw(self):
        if self.hp > 0:
            super().draw()
    def get_damage(self):
        if self.hp > 0:
            self.hp -= 1
            game.hp_bar.update()
            if self.hp == 0:
                game.explosions.add(Explosion(self.rect.centerx,self.rect.centery, self.game_over))

    def game_over(self):
        game.state = 'over'


    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_d] and self.rect.right < WIDTH:
            self.rect.x += self.speed    
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= self.speed    
        if keys[pygame.K_s] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed    
        if self.shoot_cd.done(False) and keys[pygame.K_r]:
            self.shoot_cd.reset()
            game.player_lasers.add(
                Laser(
                    self.rect.left,
                    self.rect.centery,
                    RED,
                    -5
                )
            )
            game.player_lasers.add(
                Laser(
                    self.rect.right,
                    self.rect.centery,
                    RED,
                    -5
                )
            )
        collided_enemy = pygame.sprite.spritecollideany(self, game.enemies)
        if collided_enemy:
            collided_enemy.hp = 1
            collided_enemy.get_damage()
            self.hp = 1
            self.get_damage()
        collided_laser = pygame.sprite.spritecollideany(self,game.enemy_lasers)
        if collided_laser:
            collided_laser.kill()
            self.get_damage()



class Enemy(SpaceShip):
    def __init__(self):
        enemy_class = random.randint(1, 12)
        if enemy_class <= 11:

            super().__init__(image='jedi-ship.png', x = random.randint(50, WIDTH - 50), y = -50, speed = 2, hp = 1)
        if enemy_class == 12:
            super().__init__(image='better_enemy.png', x = random.randint(50, WIDTH - 50), y = -50, speed = 1.5, hp = 3)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()
        collided_laser = pygame.sprite.spritecollideany(self,game.player_lasers)
        if collided_laser:
            collided_laser.kill()
            self.get_damage()
        if self.shoot_cd.done():
            game.enemy_lasers.add(
                Laser(
                    self.rect.centerx,
                    self.rect.centery,
                    BLUE,
                    6
                )
            )

    def get_damage(self):
        self.hp -= 1

        if self.hp == 0:
            self.kill()
            game.explosions.add(Explosion(self.rect.centerx, self.rect.centery))
            game.score += self.max_hp
            game.score_label.update(str(game.score))


class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y, color, speed):
        super().__init__()
        self.image = pygame.Surface((3, 15))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT or self.rect.bottom < 0:
            self.kill()


class Hpbar():
    def __init__(self):
        self.bg = pygame.Surface((200, 10))
        self.bg.fill(BLACK)
        self.hp = pygame.Surface((200, 10))
        self.hp.fill(RED)
        self.rect = self.bg.get_rect(bottomleft = (20, HEIGHT - 20))


    def draw(self):
        window.blit(self.bg, self.rect)
        window.blit(self.hp, self.rect)

    def update(self):
        size = game.player.hp * (self.bg.get_width() // game.player.max_hp)
        self.hp = pygame.Surface((size, 10))
        self.hp.fill(RED)





class GameManager():
    def __init__(self):
        self.score = 0
        self.state = 'play'
        self.bg = pygame.image.load('bg.jpg')
        self.player = Player()
        self.score_label = Text('0', 25, 30, 30)
        self.enemies = pygame.sprite.Group()
        self.enemy_spawn_cd = Cooldown(TICKRATE/4)
        self.player_lasers = pygame.sprite.Group()
        self.enemy_lasers = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.hp_bar = Hpbar()
        self.over_label = Text('Kanec', 50, WIDTH // 2, HEIGHT // 2)
        self.restart_label = Text('Najmi C dla restart', 30, WIDTH // 2, HEIGHT // 2 + 50)
    def spawn_enemy(self):
        if self.enemy_spawn_cd.done():
            self.enemies.add(Enemy())

    def restart(self):
        self.__init__()
    def draw(self):
        window.blit(self.bg, (0, 0))
        self.player.draw()
        self.enemies.draw(window)
        self.player_lasers.draw(window)
        self.score_label.draw()
        self.enemy_lasers.draw(window)
        self.explosions.draw(window)
        self.hp_bar.draw()
        if self.state == 'over':
            self.over_label.draw()
            self.restart_label.draw()
    def update(self):
        if self.state == 'play':

            self.player.update()
            self.enemies.update()
            self.spawn_enemy()
            self.player_lasers.update()
            self.enemy_lasers.update()
            self.explosions.update()
            pygame.sprite.groupcollide(self.player_lasers, self.enemy_lasers, True, True)
game = GameManager()

while True:
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT:
            quit()
        if e.type == pygame.KEYDOWN:
            if game.state == 'over'and e.key == pygame.K_c:
                game.restart()

    game.draw()
    game.update()
    pygame.display.flip()
    clock.tick(TICKRATE)