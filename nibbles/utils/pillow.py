import io

from discord import File
from PIL import Image, ImageFont, ImageDraw

from nibbles.config import media_dir

WHITE = (0, 0, 0)

title_font = ImageFont.truetype(str(media_dir.joinpath('fonts').joinpath('TuesdayJingle.ttf')), 160)
subtitle_font = ImageFont.truetype(str(media_dir.joinpath('fonts').joinpath('TuesdayJingle.ttf')), 120)
body_font = ImageFont.truetype(str(media_dir.joinpath('fonts').joinpath('ACT.ttf')), 100)
hand_font = ImageFont.truetype(str(media_dir.joinpath('fonts').joinpath('Kitnoms-Regular.ttf')), 45)


def generate_lb(ranks, names, pts):
    bg = Image.open(media_dir.joinpath('background').joinpath('leaderboard.png')).convert('RGBA')

    text_layer = Image.new('RGBA', bg.size)
    txt = ImageDraw.Draw(text_layer)

    txt.text((45, 125), ranks, WHITE, font=hand_font, spacing=24)
    txt.text((90, 125), names, WHITE, font=hand_font, spacing=24)
    txt.text((350, 125), pts, WHITE, font=hand_font, spacing=24)
    bg = Image.alpha_composite(bg, text_layer)
    with io.BytesIO() as image_binary:
        bg.save(image_binary, 'PNG')
        image_binary.seek(0)
        return File(fp=image_binary, filename='leaderboard.png')
