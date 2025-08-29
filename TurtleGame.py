import turtle
import random
import math

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SPEED = 30
OBSTACLE_COUNT = 20
TIMER_START = 30

class Game:
    def __init__(self):
        # Screen setup
        self.screen = turtle.Screen()
        self.screen.bgcolor("lightblue")
        self.screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)

        self.x_limit = self.screen.window_width() // 2 - 20
        self.y_limit = self.screen.window_height() // 2 - 20

        # Game state
        self.score = 0
        self.time_left = TIMER_START
        self.running = True

        # Create objects
        self.player = Player(self)
        self.goal = Goal(self)
        self.obstacles = [Obstacle(self) for _ in range(OBSTACLE_COUNT)]

        # Score & Timer UI
        self.score_display = UI(self, 0, self.y_limit - 30, f"Score: {self.score}")
        self.timer_display = UI(self, 0, self.y_limit - 60, f"Time: {self.time_left}")
        self.game_over_display = UI(self, 0, 0, "")
        self.play_again_button = Button(self)

        # Controls
        self.screen.listen()
        self.screen.onkey(self.player.move_left, "Left")
        self.screen.onkey(self.player.move_right, "Right")
        self.screen.onkey(self.player.move_up, "Up")
        self.screen.onkey(self.player.move_down, "Down")
        self.screen.onclick(self.play_again_button.check_click)

        # Start loops
        self.check_collision()
        self.move_obstacles()
        self.update_timer()
        self.player.move()
        self.screen.mainloop()

    # Game logic 
    def update_score(self):
        self.score_display.update(f"Score: {self.score}")

    def update_timer(self):
        if not self.running:
            return
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_display.update(f"Time: {self.time_left}")
            if self.running:
                self.screen.ontimer(self.update_timer, 1000)
        else:
            self.end_game()

    def check_collision(self):
        if not self.running:
            return
        if self.time_left <= 0:
            return

        # Goal collision
        if self.player.t.distance(self.goal.t) < 20:
            self.score += 1
            self.update_score()
            self.goal.reset_position()

        # Obstacle collision
        for obs in self.obstacles:
            if self.player.t.distance(obs.t) < 20:
                self.score -= 1
                self.update_score()
                obs.reset_position()

        if self.running:
            self.screen.ontimer(self.check_collision, 100)

    def move_obstacles(self):
        if not self.running:
            return
        for obs in self.obstacles:
            obs.move()
        if self.running:
            self.screen.ontimer(self.move_obstacles, 300)

    def end_game(self):
        self.running = False
        self.game_over_display.update(f"Game Over!\nFinal Score: {self.score}", font=("Arial", 24, "bold"))
        self.play_again_button.show()

    def restart(self):
        self.score = 0
        self.time_left = TIMER_START
        self.running = True
        self.update_score()
        self.timer_display.update(f"Time: {self.time_left}")
        self.game_over_display.clear()
        self.play_again_button.hide()
        self.player.reset()
        self.goal.reset_position()

        for obs in self.obstacles:
            obs.reset_position()

        self.screen.ontimer(self.check_collision, 100)
        self.screen.ontimer(self.move_obstacles, 300)
        self.screen.ontimer(self.update_timer, 1000)
        self.screen.ontimer(self.player.move, 100)

class Player:
    def __init__(self, game):
        self.game = game
        self.t = turtle.Turtle()
        self.t.shape("turtle")
        self.t.color("green")
        self.t.penup()
        self.direction = "stop"

    def reset(self):
        self.t.goto(0, 0)
        self.direction = "stop"

    def keep_in_bounds(self):
        x, y = self.t.xcor(), self.t.ycor()
        if x > self.game.x_limit: 
            self.game.screen.tracer(0)
            self.t.setx(-self.game.x_limit)
            self.game.screen.tracer(1)
        elif x < -self.game.x_limit: 
            self.game.screen.tracer(0)
            self.t.setx(self.game.x_limit)
            self.game.screen.tracer(1)
        if y > self.game.y_limit: 
            self.game.screen.tracer(0)
            self.t.sety(-self.game.y_limit)
            self.game.screen.tracer(1)
        elif y < -self.game.y_limit: 
            self.game.screen.tracer(0)
            self.t.sety(self.game.y_limit)
            self.game.screen.tracer(1)

    def move(self):
        self.game.screen.tracer(0)
        if self.direction == "left":
            self.t.setheading(180)
        elif self.direction == "right":
            self.t.setheading(0)
        elif self.direction == "up":
            self.t.setheading(90)
        elif self.direction == "down":
            self.t.setheading(270)

        if self.direction != "stop":
            self.t.forward(20)
            self.keep_in_bounds()

        if self.game.running:
            self.game.screen.ontimer(self.move, 100)
        self.game.screen.tracer(1)

    def move_left(self):
        self.direction = "left"

    def move_right(self):
        self.direction = "right"

    def move_up(self):
        self.direction = "up"

    def move_down(self):
        self.direction = "down"

class Goal:
    def __init__(self, game):
        self.game = game
        self.t = turtle.Turtle()
        self.t.shape("circle")
        self.t.color("green")
        self.t.penup()
        self.reset_position()

    # def reset_position(self):
    #     self.game.screen.tracer(0)
    #     self.t.goto(random.randint(-self.game.x_limit, self.game.x_limit),
    #                 random.randint(-self.game.y_limit, self.game.y_limit))
    #     self.game.screen.tracer(1)

    def reset_position(self):
        obstacles = getattr(self.game, "obstacles", [])  
        x_limit, y_limit = self.game.x_limit, self.game.y_limit

        for _ in range(80):
            x = random.randint(-x_limit, x_limit)
            y = random.randint(-y_limit, y_limit)

            dist_player = math.hypot(x - self.game.player.t.xcor(), y - self.game.player.t.ycor())
            if dist_player < 50:
                continue

            too_close = False
            for obs in obstacles:
                if math.hypot(x - obs.t.xcor(), y - obs.t.ycor()) < 35:  # >20 collision radius
                    too_close = True
                    break

            if not too_close:
                self.t.goto(x, y)
                return

        # Fallback
        self.t.goto(0, 0)

class Obstacle:
    def __init__(self, game):
        self.game = game
        self.t = turtle.Turtle()
        self.t.shape("square")
        self.t.color("red")
        self.t.penup()
        self.reset_position()

    def reset_position(self):
        while True:
            x = random.randint(-self.game.x_limit, self.game.x_limit)
            y = random.randint(-self.game.y_limit, self.game.y_limit)
            self.game.screen.tracer(0)
            self.t.goto(x, y)
            if self.t.distance(self.game.player.t) >= 50 and self.t.distance(self.game.goal.t) >= 50:
                break
            self.game.screen.tracer(1)

    def move(self):
        self.t.setheading(random.choice([0, 90, 180, 270]))
        self.t.forward(10)
        self.keep_in_bounds()

    def keep_in_bounds(self):
        x, y = self.t.xcor(), self.t.ycor()
        self.game.screen.tracer(0)
        if x > self.game.x_limit: 
            self.t.setx(-self.game.x_limit)
        if x < -self.game.x_limit: 
            self.t.setx(self.game.x_limit)
        if y > self.game.y_limit: 
            self.t.sety(-self.game.y_limit)
        if y < -self.game.y_limit: 
            self.t.sety(self.game.y_limit)
        self.game.screen.tracer(1)

class UI:
    def __init__(self, game, x, y, text, font=("Arial", 16, "bold")):
        self.t = turtle.Turtle()
        self.t.hideturtle()
        self.t.penup()
        self.t.goto(x, y)
        self.font = font
        self.update(text)

    def update(self, text, font=None):
        self.t.clear()
        self.t.write(text, align="center", font=font or self.font)

    def clear(self):
        self.t.clear()

class Button:
    def __init__(self, game):
        self.game = game
        self.t = turtle.Turtle()
        self.t.hideturtle()
        self.t.penup()
        self.button_area = (-60, -70, 60, -30)  # x1, y1, x2, y2

    def show(self):
        self.t.goto(-60, -70)
        self.t.color("yellow")
        self.t.begin_fill()
        for _ in range(2):
            self.t.forward(120)
            self.t.left(90)
            self.t.forward(40)
            self.t.left(90)
        self.t.end_fill()
        self.t.goto(0, -65)
        self.t.color("black")
        self.t.write("PLAY AGAIN", align="center", font=("Arial", 16, "bold"))

    def hide(self):
        self.t.clear()

    def check_click(self, x, y):
        x1, y1, x2, y2 = self.button_area
        if x1 <= x <= x2 and y1 <= y <= y2:
            self.game.restart()

Game()
