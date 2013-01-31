"""Renders a gentle snowfall animation."""

import math
import pygame
import pygame.gfxdraw
import random

# The RGB color of the background.
BACKGROUND_COLOR = (18, 26, 40)
# The filename of an optional background image. Can be None.
BACKGROUND_IMAGE = 'bg.png'
# The base color of the snowflakes.
FOREGROUND_COLOR = (175, 184, 195)
# The window width.
WIDTH = 1200
# The window height.
HEIGHT = 600
# The width in pixels of the bottom margin of the window. When snowflakes reach
# this margin, they begin to fade away.
EDGE_MARGIN = 40
# The total number of snowflake particles.
TOTAL_FLAKES = 400
# The number of particle layers. The snowflakes of each layer in the set is one
# pixel larger in radius. Earlier layers move slower, to create the illusion of
# perspective.
LAYERS = 4
# The base X  and Y speed of the snowflakes.
SPEED_BASE_X_MS = 0.02
SPEED_BASE_Y_MS = 0.07
# The maximum per-frame random variation of X and Y speeds of the snowflakes.
SPEED_VARIATION_X_MS = 0.01
SPEED_VARIATION_Y_MS = 0.02
# The minimum number of milliseconds a snowflake must move in the same
# horizontal direction before switching.
DIRECTION_CHANGE_DELAY = 2000
# The minimum lifetime of a snowflake in milliseconds. A snowflake that stays on
# the screen for longer than its lifetime respawns.
LIFETIME_BASE_MS = 4000
# The maximum random variation of the lifetime, in milliseconds.
LIFETIME_VARIATION_MS = 6000
# The number of milliseconds before death during which the snowflake fades out.
LIFETIME_FADE_THRESHOLD_MS = 750


class Snowflake(object):
    def __init__(self,
                 size,
                 lifetime,
                 speed=1.0,
                 color=FOREGROUND_COLOR,
                 opacity=1.0):
        self.size = size
        self.full_lifetime = lifetime
        self.lifetime = lifetime
        self.direction = 1 if random.random() < 0.5 else -1  # 1=right; -1=left.
        self.direction_time_remaining = random.randrange(DIRECTION_CHANGE_DELAY)
        self.x = 0
        self.y = 0
        self.color = color
        self.alpha = opacity
        self.speed = speed
        self.reposition()

    def move(self, delta_time):
        # Calculate the horizontal movement (swivel) amount.
        x_phase = self.direction_time_remaining / float(DIRECTION_CHANGE_DELAY)
        swivel_multiplier = self.direction * math.sin(x_phase * math.pi)

        # Calculate new coordinates.
        dx = SPEED_BASE_X_MS + random.random() * SPEED_VARIATION_X_MS
        dy = SPEED_BASE_Y_MS + random.random() * SPEED_VARIATION_Y_MS
        self.x += dx * swivel_multiplier * delta_time * self.speed
        self.y += dy * delta_time * self.speed

        # Account for time passage.
        self.lifetime -= delta_time
        self.direction_time_remaining -= delta_time
        if self.direction_time_remaining <= 0:
            # Time to switch direction.
            self.direction *= -1
            self.direction_time_remaining = DIRECTION_CHANGE_DELAY

        # Check if we need to respawn.
        too_right = self.x > WIDTH + self.size / 2
        too_far_down = self.y > HEIGHT + self.size / 2
        if self.lifetime <= 0 or too_right or too_far_down:
            self.lifetime = self.full_lifetime
            self.reposition(False)

    def reposition(self, allow_inside=True):
        self.x = random.randrange(WIDTH)
        if allow_inside:
            self.y = random.randrange(-self.size, HEIGHT)
        else:
            self.y = -self.size

    def draw(self, surface):
        radius = self.size
        # Walk all pixels in the square enclosing the circle and calculate the
        # correctly blended color. Very inefficient, but pretty.
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                self._drawPixel(surface, dx, dy)

    def _drawPixel(self, surface, dx, dy):
        radius = self.size
        # Calculate distance from the pixel (fit to grid) to the center.
        y = int(self.y + dy)
        x = int(self.x + dx)
        dx = x - self.x
        dy = y - self.y
        unit_distance = math.hypot(dx, dy) / radius
        if unit_distance <= 1:
            # Fade out outwards from the center.
            alpha = self.alpha * (1 - unit_distance)
            # Fade out at bottom edge and before life ends.
            edge_distance = max(0, min(EDGE_MARGIN, HEIGHT - y))
            edge_fade = float(edge_distance) / EDGE_MARGIN
            life_fade = min(1, float(self.lifetime) /
                                     LIFETIME_FADE_THRESHOLD_MS)
            alpha *= min(life_fade, edge_fade)
            # Draw pixel.
            pygame.gfxdraw.pixel(surface, x, y, self.color + (alpha * 255,))


def run_game():
    # Initialize the window.
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption('Snow, with a touch of Shinkai')

    # Create a clock to keep track of animation speed.
    clock = pygame.time.Clock()

    # Initialize the flakes.
    snowflakes = []
    for index in range(TOTAL_FLAKES):
        layer = 1 + int(float(index) / TOTAL_FLAKES * LAYERS)
        speed = layer / float(LAYERS)
        lifetime = LIFETIME_BASE_MS + random.randint(0, LIFETIME_VARIATION_MS)
        lifetime /= speed  # Flakes that move slower live longer.
        opacity = 0.25 + random.random() * 0.75
        snowflake = Snowflake(size=layer,
                              speed=speed,
                              lifetime=lifetime,
                              opacity=opacity)
        snowflakes.append(snowflake)

    # Initialize the background if needed.
    if BACKGROUND_IMAGE:
        bg_image = pygame.image.load(BACKGROUND_IMAGE).convert()
    else:
        bg_image = None

    # Main loop.
    while True:
        # Check for the user closing the program.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        # Move.
        delta_time = clock.tick()
        for snowflake in snowflakes:
            snowflake.move(delta_time)

        # Draw.
        screen.fill(BACKGROUND_COLOR)
        if bg_image:
            screen.blit(bg_image, bg_image.get_rect())
        for snowflake in snowflakes:
            snowflake.draw(screen)

        # Next frame.
        pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    try:
        run_game()
    finally:
        pygame.quit()
