from flask import Flask, request, send_file
import os
import requests
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip
import uuid

app = Flask(__name__)

def download_file(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)
    return filename

@app.route("/", methods=["POST"])
def assemble_video():
    try:
        data = request.json
        if not data:
            return {"error": "Aucune donnée reçue"}, 400

        images = data.get("images", [])[:5]
        voice_url = data.get("voice")
        music_url = data.get("music")
        output_name = data.get("output", f"zap_{uuid.uuid4()}.mp4")

        if not images or not voice_url or not music_url:
            return {"error": "images, voice et music sont requis"}, 400

        temp_files = []
        clips = []

        for i, url in enumerate(images):
            image_filename = f"image_{i}.jpg"
            download_file(url, image_filename)
            temp_files.append(image_filename)

            img_clip = ImageClip(image_filename, duration=2)
            img_clip = img_clip.resize(height=1920).set_position("center")
            clips.append(img_clip)

        video = concatenate_videoclips(clips, method="compose")

        voice_path = "voice.mp3"
        download_file(voice_url, voice_path)
        temp_files.append(voice_path)
        voice_audio = AudioFileClip(voice_path)

        music_path = "music.mp3"
        download_file(music_url, music_path)
        temp_files.append(music_path)
        music_audio = AudioFileClip(music_path).volumex(0.3)

        final_audio = CompositeAudioClip([voice_audio, music_audio.set_start(0)])
        video = video.set_audio(final_audio)

        output_dir = "videos"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_name)
        video.write_videofile(output_path, fps=24)

        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return {"error": str(e)}, 500

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
