import os
from PIL import Image

SRC = '/Users/kyungju/Downloads/honClimber.png'
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs', 'assets')

im = Image.open(SRC).convert('RGBA')
w, h = im.size
px = im.load()

# 배경(흰색)과 그림자(무채색 회색)는 채도가 낮고, 클라이밍 홀드는 채도가 높다.
# 채도 기준으로 배경/그림자를 함께 투명 처리한다.
SAT_LOW = 18    # 이 채도 이하면 완전 투명 (배경/그림자)
SAT_HIGH = 55   # 이 채도 이상이면 완전 불투명 (홀드 본체)

for y in range(h):
    for x in range(w):
        r, g, b, a = px[x, y]
        saturation = max(r, g, b) - min(r, g, b)
        if saturation <= SAT_LOW:
            alpha = 0
        elif saturation >= SAT_HIGH:
            alpha = 255
        else:
            alpha = int(255 * (saturation - SAT_LOW) / (SAT_HIGH - SAT_LOW))
        px[x, y] = (r, g, b, min(a, alpha))

bbox = im.getbbox()
if bbox:
    pad = 30
    l, t, r2, b2 = bbox
    l = max(0, l - pad); t = max(0, t - pad)
    r2 = min(w, r2 + pad); b2 = min(h, b2 + pad)
    im = im.crop((l, t, r2, b2))

os.makedirs(OUT_DIR, exist_ok=True)
im.resize((256, 256), Image.LANCZOS).save(os.path.join(OUT_DIR, 'favicon.png'))
print('favicon saved', im.size)
