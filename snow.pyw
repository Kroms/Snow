"""Renders a gentle snowfall animation."""

import math
import pygame
import random

# The RGB color of the background.
BACKGROUND_COLOR = (18, 26, 40)
# The filename of an optional background image. Can be None.
BACKGROUND_IMAGE = 'bg.png'
# The RGB base color of the snowflakes.
FOREGROUND_COLOR = (80, 79, 90)
# The window width.
WIDTH = 1200
# The window height.
HEIGHT = 600
# The width in pixels of the bottom margin of the window. When snowflakes reach
# this margin, they begin to fade away.
EDGE_MARGIN = 40
# The total number of snowflake particles.
TOTAL_FLAKES = 5000
# The number of particle layers. The snowflakes of each layer in the set is one
# pixel larger in radius. Earlier layers move slower, to create the illusion of
# perspective.
LAYERS = 3
# The base X  and Y speed of the snowflakes.
SPEED_BASE_X_MS = 0.02
SPEED_BASE_Y_MS = 0.05
# The maximum per-frame random variation of X and Y speeds of the snowflakes.
SPEED_VARIATION_X_MS = 0.01
SPEED_VARIATION_Y_MS = 0.04
# The minimum number of milliseconds a snowflake must move in the same
# horizontal direction before switching.
DIRECTION_CHANGE_DELAY = 2000
# The minimum lifetime of a snowflake in milliseconds. A snowflake that stays on
# the screen for longer than its lifetime respawns.
LIFETIME_BASE_MS = 4000
# The maximum random variation of the lifetime, in milliseconds.
LIFETIME_VARIATION_MS = 9000
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
        self.surface = self._renderSprite()
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
            self.y = random.randrange(-self.size * 2, HEIGHT)
        else:
            self.y = -random.randrange(self.size * 2)

    def draw(self, surface):
        # Fade out at bottom edge and before death.
        edge_distance = max(0, min(EDGE_MARGIN, HEIGHT - self.y))
        edge_fade = float(edge_distance) / EDGE_MARGIN
        life_fade = min(1, float(self.lifetime) / LIFETIME_FADE_THRESHOLD_MS)
        alpha = min(life_fade, edge_fade)

        self._blit(surface, alpha)

    def _renderSprite(self):
        sprite_radius = self.size * 2
        surface = pygame.Surface((sprite_radius * 2, sprite_radius * 2))
        # Walk all pixels in the square enclosing the circle and calculate the
        # correctly blended color.
        surface.lock()
        for dx in range(-sprite_radius, sprite_radius + 1):
            for dy in range(-sprite_radius, sprite_radius + 1):
                self._drawPixel(surface, dx, dy)
        surface.unlock()
        return surface
        
    def _drawPixel(self, surface, dx, dy):
        sprite_radius = self.size * 2
        # Calculate distance from the pixel (fit to grid) to the center.
        unit_distance = math.hypot(dx, dy) / sprite_radius
        if unit_distance < 1:
            # Fade out outwards from the center.
            alpha = self.alpha * (1 - unit_distance)
            # Draw pixel.
            x = sprite_radius + dx
            y = sprite_radius + dy
            surface.set_at((x, y), [ch * alpha for ch in self.color])
        
    def _blit(self, surface, alpha):
        sprite_radius = self.size * 2
        if alpha == 0:
            return
        elif alpha == 1:
            self.surface.set_alpha(255, pygame.RLEACCEL)
            src = self.surface
        else:
            src = pygame.Surface((sprite_radius * 2, sprite_radius * 2))
            self.surface.set_alpha(int(alpha * 255), pygame.RLEACCEL)
            src.blit(self.surface, (0, 0))
        corner = (int(self.x * 2 - sprite_radius),
                  int(self.y * 2 - sprite_radius))
        surface.blit(src, corner, None, pygame.BLEND_ADD)
        if src != self.surface:
            del src


def run_game():
    # Initialize the canvas and background if needed.
    canvas = pygame.Surface((WIDTH * 2, HEIGHT * 2))
    if BACKGROUND_IMAGE:
        raw_image = pygame.image.load(BACKGROUND_IMAGE).convert(32)
        bg_image = pygame.transform.scale2x(raw_image)
    else:
        bg_image = None

    # Initialize the window.
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF, 32)
    pygame.display.set_caption('Snow, with a touch of Shinkai')

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

    # Create a clock to keep track of animation speed.
    clock = pygame.time.Clock()

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
        canvas.fill(BACKGROUND_COLOR)
        if bg_image:
            canvas.blit(bg_image, bg_image.get_rect())
        for snowflake in snowflakes:
            snowflake.draw(canvas)
        pygame.transform.smoothscale(canvas, (WIDTH, HEIGHT), screen)

        # Next frame.
        pygame.display.flip()


def main():
    pygame.init()
    try:
        run_game()
    finally:
        pygame.quit()


if __name__ == '__main__':
    main()