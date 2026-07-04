"""
DL Form Calibration Tool
Renders the DL_correction.pdf page 0 at high resolution,
overlays a 5mm coordinate grid, and saves a PNG.
Inspect the PNG to read off exact (x,y) coordinates for each field.
"""
import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFont

PDF_PATH  = r"app\data\DL_correction.pdf"
OUT_PNG   = r"calibration_dl.png"
PAGE      = 0
SCALE     = 4          # 4x render → ~288 DPI
MM_STEP   = 5          # draw a grid line every 5 mm

# A4 dimensions in mm
A4_W_MM = 210.0
A4_H_MM = 297.0

src = pdfium.PdfDocument(PDF_PATH)
page = src[PAGE]
bitmap = page.render(scale=SCALE)
img = bitmap.to_pil().convert("RGB")
W, H = img.size

# mm → pixel conversion
def mm2px(mm_x, mm_y):
    px = int(mm_x / A4_W_MM * W)
    py = int(mm_y / A4_H_MM * H)
    return px, py

draw = ImageDraw.Draw(img)

# Draw grid
try:
    font = ImageFont.truetype("arial.ttf", 18)
    small_font = ImageFont.truetype("arial.ttf", 14)
except:
    font = ImageFont.load_default()
    small_font = font

x_mm = 0
while x_mm <= A4_W_MM:
    px, _ = mm2px(x_mm, 0)
    draw.line([(px, 0), (px, H)], fill=(180, 180, 255) if x_mm % 10 == 0 else (220, 220, 255), width=1)
    if x_mm % 10 == 0 and x_mm > 0:
        draw.text((px + 2, 2), f"{x_mm}", fill=(0, 0, 180), font=small_font)
    x_mm += MM_STEP

y_mm = 0
while y_mm <= A4_H_MM:
    _, py = mm2px(0, y_mm)
    draw.line([(0, py), (W, py)], fill=(180, 255, 180) if y_mm % 10 == 0 else (220, 255, 220), width=1)
    if y_mm % 10 == 0 and y_mm > 0:
        draw.text((2, py + 2), f"{y_mm}", fill=(0, 130, 0), font=small_font)
    y_mm += MM_STEP

img.save(OUT_PNG, "PNG")
print(f"Saved calibration grid to: {OUT_PNG}")
print(f"Image size: {W} x {H} px  (represents {A4_W_MM} x {A4_H_MM} mm)")
print(f"Scale: {SCALE}x  (so 1 mm ≈ {W/A4_W_MM:.1f} px horizontally)")
