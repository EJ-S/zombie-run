"""
A simple game made using python arcade
"""

import arcade
import math
import random
import os
from arcade.key import ENTER

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = 'look at mouse'
MOVEMENT_SPEED = 5
ZOMBIE_SPEED = 2
BULLET_SPEED = 20
NUM_ZOMBIES = 15
TOTAL_ZOMBIES = 20

class Player(arcade.Sprite):

    def __init__(self, image, scale):

        super().__init__(image, scale)
        self.mouse_y = 0
        self.mouse_x = 0

    
    def update(self):
        
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Move player to other side of screen if going off the screen
        if self.center_x < 0:
            self.center_x = SCREEN_WIDTH - 1
        elif self.center_x > SCREEN_WIDTH - 1:
            self.center_x = 0

        if self.center_y < 0:
            self.center_y = SCREEN_HEIGHT - 1
        elif self.center_y > SCREEN_HEIGHT - 1:
            self.center_y = 0

        # Make player look at mouse
        diff_x = self.mouse_x - self.center_x
        diff_y = self.mouse_y - self.center_y
        ang = math.degrees(math.atan2(diff_y, diff_x))
        self.angle = ang


class StartView(arcade.View):

    def __init__(self):

        super().__init__()
        self.texture = arcade.load_texture(".\Resources\StartTest.png")
    
    def on_draw(self):
        arcade.start_render()
        arcade.draw_texture_rectangle(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, SCREEN_WIDTH, SCREEN_HEIGHT, self.texture)
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)


class EndView(arcade.View):

    def __init__(self, score):

        super().__init__()
        self.texture = arcade.load_texture(".\Resources\EndTest.png")
        self.score = score
    
    def on_draw(self):
        arcade.start_render()
        arcade.draw_texture_rectangle(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, SCREEN_WIDTH, SCREEN_HEIGHT, self.texture)
        s = "Your Score: {}".format(self.score)
        arcade.draw_text(s, 710, 400, (155, 173, 183), 40, font_name="Kenney Pixel Square")
        arcade.draw_text("Press ESC to close", 620, 300, (155, 173, 183), 40, font_name="Kenney Pixel Square")

    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)
        if key == arcade.key.ESCAPE:
            self.window.close()

class GameView(arcade.View):

    def __init__(self):

        super().__init__()

        self.player_list = None
        self.bullet_list = None
        self.player_sprite = None
        self.gore_list = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Track num zombies spawned
        self.zombies_spawned = NUM_ZOMBIES

        self.health = 10
        self.score = 0

        # Load Sounds
        self.gun_sound = arcade.load_sound(".\Resources\gunSound.mp3")
        self.hit_sound = arcade.load_sound(".\Resources\hitSound.mp3")
        self.zombie_hit = arcade.load_sound(".\Resources\zombieHit.mp3")

        self.window.set_fullscreen(True)

        self.background = arcade.load_texture(".\Resources\GrassTest2.png")


    def setup(self):

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.zombie_list = arcade.SpriteList()
        self.gore_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = Player(".\Resources\TopTest.png", 0.5)
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = SCREEN_HEIGHT / 2
        self.player_list.append(self.player_sprite)

        for i in range(NUM_ZOMBIES):
            zombie = arcade.Sprite(".\Resources\ZombieTest.png", 0.5)
            zombie.center_x = random.randrange(SCREEN_WIDTH)
            zombie.center_y = random.randrange(SCREEN_HEIGHT)
            self.zombie_list.append(zombie)


    def on_draw(self):

        arcade.start_render()
        arcade.draw_texture_rectangle(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 1920, 1080, self.background)
        self.gore_list.draw()
        self.bullet_list.draw()
        self.player_list.draw()
        self.zombie_list.draw()
        
        hp = 'HP: {}'.format(self.health)
        s = 'Score: {}'.format(self.score)
        arcade.draw_text(hp, 100, 900, arcade.color.DARK_LAVA, 30, font_name="Kenney Pixel Square")
        arcade.draw_text(s, 100, 800, arcade.color.DARK_LAVA, 30, font_name="Kenney Pixel Square")
        
    
    def update_player_speed(self):

        # Calculate speed based on the keys pressed
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -MOVEMENT_SPEED
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = MOVEMENT_SPEED

    def on_update(self, delta_time):

        self.player_list.update()
        self.bullet_list.update()
        self.zombie_list.update()

        # To get zombies to look at player and act
        for zombie in self.zombie_list:
            diff_x = self.player_sprite.center_x - zombie.center_x
            diff_y = self.player_sprite.center_y- zombie.center_y
            ang = math.atan2(diff_y, diff_x)
            zombie.angle = math.degrees(ang)
            zombie.change_x = math.cos(ang) * (ZOMBIE_SPEED+ 0.01 * self.score) 
            zombie.change_y = math.sin(ang) * (ZOMBIE_SPEED+ 0.01 * self.score) 
            hit = arcade.check_for_collision(zombie, self.player_sprite)
            if hit:
                zombie.remove_from_sprite_lists()
                self.health -= 1
                arcade.play_sound(self.hit_sound)
        
        # Check for bullets
        for bullet in self.bullet_list:
            hits = arcade.check_for_collision_with_list(bullet, self.zombie_list)
            if len(hits) > 0:
                bullet.remove_from_sprite_lists()
            for zombie in hits:
                gore = arcade.Sprite(".\Resources\GoreTest.png")
                gore.center_y = zombie.center_y
                gore.center_x = zombie.center_x
                self.gore_list.append(gore)
                zombie.remove_from_sprite_lists()
                self.score += 1
                arcade.play_sound(self.zombie_hit)

            if bullet.bottom > SCREEN_WIDTH or bullet.top < 0 or bullet.right < 0 or bullet.left > SCREEN_WIDTH:
                bullet.remove_from_sprite_lists()

        # Add more zombies
        for i in range(NUM_ZOMBIES-len(self.zombie_list)):
            zombie = arcade.Sprite(".\Resources\ZombieTest.png", 0.5)
            if random.random() < 0.65:
                zombie.center_x = random.randrange(SCREEN_WIDTH)
                zombie.center_y = (random.randrange(-100, 0), random.randrange(SCREEN_HEIGHT,SCREEN_HEIGHT+100))[random.random() < 0.5]
            else:
                zombie.center_x = (random.randrange(-100, 0), random.randrange(SCREEN_WIDTH,SCREEN_WIDTH+100))[random.random() < 0.5]
                zombie.center_y = random.randrange(SCREEN_HEIGHT)
            self.zombie_list.append(zombie)
            self.zombies_spawned += 1
        
        if self.health <= 0:
            end_view = EndView(self.score)
            self.window.show_view(end_view)

    
    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.player_sprite.mouse_x = x
        self.player_sprite.mouse_y = y
    
    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            bullet = arcade.Sprite(".\Resources\BulletTest.png", 0.5)
            bullet.center_x = self.player_sprite.center_x
            bullet.center_y = self.player_sprite.center_y
            diff_x = x - self.player_sprite.center_x
            diff_y = y - self.player_sprite.center_y
            ang = math.atan2(diff_y, diff_x)
            bullet.angle = math.degrees(ang)
            bullet.change_x = math.cos(ang) * BULLET_SPEED
            bullet.change_y = math.sin(ang) * BULLET_SPEED
            self.bullet_list.append(bullet)
            arcade.play_sound(self.gun_sound)
            
    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.ESCAPE:        
            self.window.set_fullscreen(not self.window.fullscreen)
        if key == arcade.key.W:
            self.up_pressed = True
            self.update_player_speed()
        elif key == arcade.key.S:
            self.down_pressed = True
            self.update_player_speed()
        elif key == arcade.key.A:
            self.left_pressed = True
            self.update_player_speed()
        elif key == arcade.key.D:
            self.right_pressed = True
            self.update_player_speed()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.W:
            self.up_pressed = False
            self.update_player_speed()
        elif key == arcade.key.S:
            self.down_pressed = False
            self.update_player_speed()
        elif key == arcade.key.A:
            self.left_pressed = False
            self.update_player_speed()
        elif key == arcade.key.D:
            self.right_pressed = False
            self.update_player_speed()





def main():
    file_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(file_path)
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.set_fullscreen(True)
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()