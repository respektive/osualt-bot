from PIL import Image
import io
from colorsys import rgb_to_hsv, hsv_to_rgb
import numpy as np
from sklearn.cluster import KMeans

TORUS_REGULAR = "src/resources/fonts/torus/Torus-Regular.otf"
TORUS_BOLD = "src/resources/fonts/torus/Torus-Bold.otf"
TORUS_SEMIBOLD = "src/resources/fonts/torus/Torus-SemiBold.otf"


# Colors taken from flyte's Tier Colours Design
# https://www.figma.com/file/YHWhp9wZ089YXgB7pe6L1k/Tier-Colours
def get_rank_tier(rank):
    # unranked players
    if not rank or rank < 1:
        colors = [(219, 240, 233)]
        font_path = TORUS_REGULAR
    # Lustrous
    elif rank == 1:
        colors = [(255, 230, 0), (237, 130, 255)]
        font_path = TORUS_BOLD
    # Radiant
    elif rank <= 10:
        colors = [(151, 220, 255), (237, 130, 255)]
        font_path = TORUS_BOLD
    # Platinum
    elif rank <= 50:
        colors = [(168, 240, 239), (82, 224, 223)]
        font_path = TORUS_BOLD
    # Gold
    elif rank <= 100:
        colors = [(240, 228, 168), (224, 201, 82)]
        font_path = TORUS_BOLD
    # Silver
    elif rank <= 500:
        colors = [(224, 224, 235), (163, 163, 194)]
        font_path = TORUS_BOLD
    # Bronze
    elif rank <= 1_000:
        colors = [(184, 143, 122), (133, 92, 71)]
        font_path = TORUS_SEMIBOLD
    # Iron
    elif rank <= 5_000:
        colors = [(186, 178, 171)]
        font_path = TORUS_REGULAR
    # Anyone else
    else:
        colors = [(219, 240, 233)]
        font_path = TORUS_REGULAR

    return {"colors": colors, "font_path": font_path}


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

    return new_image


def adjust_color_saturation_and_brightness(rgb_color, saturation, brightness):
    hsv_color = rgb_to_hsv(*rgb_color)
    adjusted_hsv = (hsv_color[0], saturation, brightness)
    adjusted_rgb = hsv_to_rgb(*adjusted_hsv)
    normalized_rgb = [int(c * 255) for c in adjusted_rgb]
    return tuple(normalized_rgb)


def get_image_color(image_data):
    image = Image.open(io.BytesIO(image_data)).convert("RGB")

    pixels = np.array(image).reshape(-1, 3)

    kmeans = KMeans(n_init=10, n_clusters=5)
    kmeans.fit(pixels)

    cluster_centers = kmeans.cluster_centers_

    _, counts = np.unique(kmeans.labels_, return_counts=True)

    dominant_color = tuple(map(int, cluster_centers[np.argmax(counts)]))

    if dominant_color == (255, 255, 255) or dominant_color == (0, 0, 0):
        dominant_color = (255, 0, 115)  # osu! Pink

    adjusted_color = adjust_color_saturation_and_brightness(dominant_color, 0.45, 0.3)

    return adjusted_color


def calculate_corner_radius(image_width, image_height, percentage):
    min_dimension = min(image_width, image_height)
    radius = int(min_dimension * (percentage / 100))
    return radius


def convert_country_code_to_unicode(country_code):
    unicode_hex_values = [
        hex(ord(char) - 65 + 0x1F1E6)[2:].upper()
        for char in country_code.upper()
        if char.isalpha()
    ]
    return "-".join(unicode_hex_values)
