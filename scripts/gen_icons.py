import math
from PIL import Image, ImageDraw

COLOR1 = (76, 155, 255)   # #4C9BFF
COLOR2 = (49, 130, 246)   # #3182F6
WHITE = (255, 255, 255, 255)

SS = 4  # supersample factor for smooth edges

def diagonal_gradient(size, color1, color2):
    g = Image.linear_gradient('L')
    big = int(size * 1.8)
    g = g.resize((big, big), Image.BICUBIC)
    g = g.rotate(-45, resample=Image.BICUBIC, expand=False)
    w, h = g.size
    left = (w - size) // 2
    top = (h - size) // 2
    g = g.crop((left, top, left + size, top + size))
    base = Image.new('RGB', (size, size), color1)
    top_img = Image.new('RGB', (size, size), color2)
    return Image.composite(top_img, base, g)

def rounded_mask(size, radius_ratio):
    mask = Image.new('L', (size, size), 0)
    d = ImageDraw.Draw(mask)
    r = int(size * radius_ratio)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=255)
    return mask

def circle_mask(size):
    mask = Image.new('L', (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([0, 0, size - 1, size - 1], fill=255)
    return mask

def draw_glyph(draw, scale, off=(0, 0)):
    # 원본 64x64 viewBox 좌표계 기준 좌표를 scale/off로 변환
    def p(x, y):
        return (off[0] + x * scale, off[1] + y * scale)

    pts = [p(11, 43), p(23, 27), p(30.5, 36.5), p(41, 21), p(53, 43)]
    width = max(1, round(4 * scale))
    draw.line(pts, fill=WHITE, width=width, joint='curve')
    # 둥근 끝 처리를 위해 각 꼭짓점에 원을 덧그림 (선 이음새/끝 라운드 캡 효과)
    rr = width / 2
    for (x, y) in pts:
        draw.ellipse([x - rr, y - rr, x + rr, y + rr], fill=WHITE)
    # 정상의 점(클라이머)
    cx, cy = p(41, 15.5)
    cr = 4.5 * scale
    draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=WHITE)

def make_full_icon(size, round_variant=False):
    ss = size * SS
    bg = diagonal_gradient(ss, COLOR1, COLOR2).convert('RGBA')
    draw = ImageDraw.Draw(bg)
    scale = ss / 64
    draw_glyph(draw, scale)
    if round_variant:
        mask = circle_mask(ss)
    else:
        mask = rounded_mask(ss, 17 / 64)
    out = Image.new('RGBA', (ss, ss), (0, 0, 0, 0))
    out.paste(bg, (0, 0), mask)
    return out.resize((size, size), Image.LANCZOS)

def make_foreground(size):
    # 안드로이드 적응형 아이콘: 전체 캔버스의 안전영역(가운데 약 66%)에만 그림
    ss = size * SS
    img = Image.new('RGBA', (ss, ss), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    safe = ss * 0.62  # 안전 영역 한 변 길이
    offset = (ss - safe) / 2
    scale = safe / 64
    draw_glyph(draw, scale, off=(offset, offset))
    return img.resize((size, size), Image.LANCZOS)

DENSITIES = {
    'mdpi': (48, 108),
    'hdpi': (72, 162),
    'xhdpi': (96, 216),
    'xxhdpi': (144, 324),
    'xxxhdpi': (192, 432),
}

import os
RES = os.path.join(os.path.dirname(__file__), '..', 'android', 'app', 'src', 'main', 'res')

for density, (icon_size, fg_size) in DENSITIES.items():
    folder = os.path.join(RES, f'mipmap-{density}')
    make_full_icon(icon_size, round_variant=False).save(os.path.join(folder, 'ic_launcher.png'))
    make_full_icon(icon_size, round_variant=True).save(os.path.join(folder, 'ic_launcher_round.png'))
    make_foreground(fg_size).save(os.path.join(folder, 'ic_launcher_foreground.png'))
    print(f'{density}: icon {icon_size}px, foreground {fg_size}px done')

print('all icons generated')
