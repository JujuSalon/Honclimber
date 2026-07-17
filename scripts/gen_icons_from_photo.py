import os
from PIL import Image, ImageDraw

SRC = '/Users/kyungju/Downloads/honClimber.png'
RES = os.path.join(os.path.dirname(__file__), '..', 'android', 'app', 'src', 'main', 'res')

def rounded_mask(size, radius_ratio):
    ss = size * 4
    mask = Image.new('L', (ss, ss), 0)
    d = ImageDraw.Draw(mask)
    r = int(ss * radius_ratio)
    d.rounded_rectangle([0, 0, ss - 1, ss - 1], radius=r, fill=255)
    return mask.resize((size, size), Image.LANCZOS)

def circle_mask(size):
    ss = size * 4
    mask = Image.new('L', (ss, ss), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([0, 0, ss - 1, ss - 1], fill=255)
    return mask.resize((size, size), Image.LANCZOS)

src = Image.open(SRC).convert('RGBA')
# 정사각형 보장 (센터 크롭)
w, h = src.size
side = min(w, h)
left = (w - side) // 2
top = (h - side) // 2
src = src.crop((left, top, left + side, top + side))

DENSITIES = {
    'mdpi': (48, 108),
    'hdpi': (72, 162),
    'xhdpi': (96, 216),
    'xxhdpi': (144, 324),
    'xxxhdpi': (192, 432),
}

for density, (icon_size, fg_size) in DENSITIES.items():
    folder = os.path.join(RES, f'mipmap-{density}')

    icon_img = src.resize((icon_size, icon_size), Image.LANCZOS)

    # legacy 아이콘 (둥근 사각형)
    mask = rounded_mask(icon_size, 17 / 64)
    out = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
    out.paste(icon_img, (0, 0), mask)
    out.save(os.path.join(folder, 'ic_launcher.png'))

    # 라운드 아이콘 (원형)
    cmask = circle_mask(icon_size)
    out2 = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
    out2.paste(icon_img, (0, 0), cmask)
    out2.save(os.path.join(folder, 'ic_launcher_round.png'))

    # 적응형 아이콘 foreground - 캔버스 전체를 채워서 시스템이 자체 마스크 적용
    fg_img = src.resize((fg_size, fg_size), Image.LANCZOS)
    fg_img.save(os.path.join(folder, 'ic_launcher_foreground.png'))

    print(f'{density}: done')

print('all icons generated from photo')
