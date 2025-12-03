from flask import Flask, send_file
from moviepy.editor import ImageClip, concatenate_videoclips
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Crée une petite vidéo temporaire
    clip = ImageClip("https://images.pexels.com/photos/110854/pexels-photo-110854.jpeg", duration=2)
    clip = clip.resize(height=1920).set_position("center")
    video = concatenate_videoclips([clip])

    output_path = "output.mp4"
    video.write_videofile(output_path, fps=24)

    return send_file(output_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
