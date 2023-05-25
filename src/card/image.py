from PIL import Image, ImageDraw
from card.constants import IMAGE_HEIGHT, IMAGE_WIDTH
from card.background import draw_background
from card.header import draw_header
from card.body import draw_body

image = Image.new("RGBA", (IMAGE_WIDTH, IMAGE_HEIGHT), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)


# Card design is using flyte's Player Card design as a base and builds on top of it
# https://www.figma.com/file/ocltATjJqWQZBravhPuqjB/UI%2FPlayer-Card
def draw_card(user_data, avatar_data):
    draw_background(draw)
    draw_header(image, draw, user_data, avatar_data)
    draw_body(image, user_data)

    return image
