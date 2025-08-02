from PIL import Image
import ffmpeg
import os
import uuid

def add_watermark_to_image(image_path, watermark_path):
    base = Image.open(image_path).convert("RGBA")
    wm = Image.open(watermark_path).convert("RGBA")
    wm = wm.resize((150, 150))
    base.paste(wm, (20, 20), wm)
    output_path = f"watermarked_{uuid.uuid4().hex}.png"
    base.save(output_path)
    return output_path

async def add_watermark_to_video(video_path, watermark_path):
    output_path = f"watermarked_{uuid.uuid4().hex}.mp4"
    (
        ffmpeg
        .input(video_path)
        .filter("overlay", 10, 10)
        .output(output_path)
        .run(overwrite_output=True)
    )
    return output_path
