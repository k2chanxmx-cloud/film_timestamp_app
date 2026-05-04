import os
import uuid
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from flask import Flask, render_template, request, jsonify, url_for

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "static", "outputs")
FONT_PATH = os.path.join(BASE_DIR, "static", "fonts", "DS-DIGI.TTF")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===== 日付フォーマット =====
def format_date(date_str, fmt):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    y, m, d = dt.year, dt.month, dt.day

    if fmt == "film":
        return f"{m}   {d} '{str(y)[-2:]}"
    elif fmt == "dot":
        return f"{y}.{m:02}.{d:02}"
    elif fmt == "short":
        return f"{str(y)[-2:]}   {m}   {d}"

# ===== タイムスタンプ生成（リアル版）=====
def create_stamp(text, size):
    font = ImageFont.truetype(FONT_PATH, size)

    dummy = Image.new("RGBA", (3000, 800), (0, 0, 0, 0))
    draw = ImageDraw.Draw(dummy)

    bbox = draw.textbbox((0, 0), text, font=font)

    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # フォントのはみ出し対策で余白を多めに取る
    pad_x = int(size * 0.35)
    pad_y = int(size * 0.45)

    img = Image.new(
        "RGBA",
        (text_w + pad_x * 2, text_h + pad_y * 2),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(img)

    color = (255, 60, 25, 170)

    # bboxの左上がマイナスになるフォント対策
    x = pad_x - bbox[0]
    y = pad_y - bbox[1]

    draw.text((x, y), text, font=font, fill=color)

    return img

# ===== 画像処理 =====
def process_image(path, date_text):
    img = Image.open(path).convert("RGB")

    rotated = False
    if img.height > img.width:
        img = img.rotate(90, expand=True)
        rotated = True

    w, h = img.size

    font_size = int(w * 0.035)
    stamp = create_stamp(date_text, font_size)

    sw, sh = stamp.size

    x = w - sw - int(w * 0.055)
    y = h - sh - int(h * 0.065)

    base = img.convert("RGBA")
    base.alpha_composite(stamp, (x, y))

    img = base.convert("RGB")

    if rotated:
        img = img.rotate(-90, expand=True)

    return img

# ===== 画面 =====
@app.route("/")
def index():
    return render_template("index.html")

# ===== 加工API =====
@app.route("/process", methods=["POST"])
def process():
    files = request.files.getlist("photos")
    date_str = request.form.get("date")
    fmt = request.form.get("format")

    if not files or not date_str:
        return jsonify({"ok": False})

    date_text = format_date(date_str, fmt)

    result_urls = []

    for f in files:
        filename = f"{uuid.uuid4().hex}.jpg"
        save_path = os.path.join(UPLOAD_DIR, filename)
        f.save(save_path)

        img = process_image(save_path, date_text)

        out_name = f"out_{filename}"
        out_path = os.path.join(OUTPUT_DIR, out_name)
        img.save(out_path, quality=95)

        result_urls.append(url_for("static", filename=f"outputs/{out_name}"))

    return jsonify({
        "ok": True,
        "images": result_urls
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)