from card.helpers import calculate_corner_radius
from card.constants import IMAGE_HEIGHT, IMAGE_WIDTH


def draw_background(draw):
    corner_radius = calculate_corner_radius(IMAGE_WIDTH, IMAGE_HEIGHT, 5)
    draw.rounded_rectangle(
        (0, 0, IMAGE_WIDTH, IMAGE_HEIGHT), fill="#2E3835", radius=corner_radius
    )
