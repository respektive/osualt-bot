import drawsvg as draw
from PIL import Image, ImageDraw
import io
import os
from dotenv import load_dotenv
load_dotenv()

# need this for dev on my windows machine, because PATH is broken idk
vipshome = os.getenv("VIPSHOME")
if vipshome:
    os.environ["PATH"] = vipshome + ";" + os.environ["PATH"]
import pyvips


def fit_image_to_aspect_ratio(image_input, aspect_ratio):
    if isinstance(image_input, str):
        image = Image.open(image_input)
    else:
        image = Image.open(io.BytesIO(image_input))

    image_width, image_height = image.size
    target_width = int(min(image_width, image_height * aspect_ratio))
    target_height = int(min(image_height, image_width / aspect_ratio))

    new_image = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
    new_image.paste(
        image, ((target_width - image_width) // 2, (target_height - image_height) // 2)
    )

    corner_radius = int(min(target_width, target_height) * 0)

    mask = Image.new("L", (target_width, target_height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(
        [(0, 0), (target_width, target_height)], corner_radius, fill=255
    )
    new_image_with_rounded_corners = Image.new("RGBA", (target_width, target_height))
    new_image_with_rounded_corners.paste(new_image, mask=mask)

    image_stream = io.BytesIO()

    new_image_with_rounded_corners.save(image_stream, format="PNG")

    image_stream.seek(0)

    image_data = image_stream.read()

    return image_data


d = draw.Drawing(375, 235)


def draw_background():
    bg = draw.Rectangle(0, 0, 375, 235, rx="10", ry="10", fill="#2E3835")
    d.append(bg)


def draw_header_background():
    mask = draw.Mask()
    box = draw.Rectangle(0, 0, 375, 60, rx="10", ry="10", fill="white")
    mask.append(box)
    data = fit_image_to_aspect_ratio("src/resources/images/default_cover.png", 375 / 60)
    header_bg = draw.Image(0, 0, 375, 60, data=data, mask=mask)
    d.append(header_bg)

    gradient = draw.LinearGradient(0, 0, 375, 60)
    gradient.add_stop(0, "#243842")
    gradient.add_stop(1, "#243342", 0.6)
    d.append(draw.Rectangle(0, 0, 375, 60, fill=gradient, rx="10", ry="10"))


def draw_avatar(image_data):
    mask = draw.Mask()
    box = draw.Rectangle(0, 0, 60, 60, rx="10", ry="10", fill="white")
    mask.append(box)
    avatar = draw.Image(0, 0, 60, 60, data=image_data, mask=mask)
    d.append(avatar)


def draw_username(username):
    text = draw.Text(username, 16, 78, 22, font_weight="600", fill="white", font_family="Torus")
    d.append(text)


def draw_osu_logo():
    outer = draw.Circle(86, 44, 8, fill="none", stroke_width=1.5, stroke="white")
    d.append(outer)

    inner = draw.Circle(86, 44, 5.5, fill="white")
    d.append(inner)


def draw_follower_count(amount):
    amount_string = f"{amount:,}"
    box = draw.Rectangle(110, 35, len(amount_string) * 6 + 23, 18, rx=9, fill="black", fill_opacity=0.5)
    d.append(box)
    icon = draw.Image( 116, 39, 10, 10, path="src/resources/images/user-solid.png", embed=True)
    d.append(icon)
    count = draw.Text(amount_string, 12, 128, 48, fill="white", font_family="Torus", font_weight="600")
    d.append(count)


def draw_header(user_data, avatar_data):
    draw_avatar(avatar_data)
    draw_username(user_data["username"])
    draw_osu_logo()
    draw_follower_count(user_data["follower_count"])


def save_file(path):
    d.set_pixel_scale(3)
    d.save_svg(path)


def convert_to_png(svg_path, png_path):
    image = pyvips.Image.new_from_file(svg_path, dpi=100)
    image.write_to_file(png_path)


def draw_card(user_data, avatar_data):
    user_id = user_data["user_id"]
    draw_background()
    draw_header_background()
    draw_header(user_data, avatar_data)
    svg_path = f"card_{user_id}.svg"
    png_path = f"card_{user_id}.png"
    save_file(svg_path)
    convert_to_png(svg_path, png_path)
    return png_path
