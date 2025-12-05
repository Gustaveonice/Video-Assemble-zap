from flask import Flask, request, jsonify
from threading import Thread
import os
import time
import requests
import uuid
from moviepy.editor import *
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DISCORD_WEBHOOK = os.getenv("https://discord.com/api/webhooks/1446531572273643756/DAYNozqSyHlSXpXG-309gOMlnsyBKAKjrBJOzJzTM05bqBwvHQbqvBJfEm99Azodik9D")  # à définir dans ton .env

def send_discord_message(content):
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": content})
    except:
        pass

def generate_video(job_id, images, voice_path, music_path, subtitle_text):
    try:
        send_discord_message(f"🎬 Job {job_id} : création vidéo en cours...")

        clips = [ImageClip(img).set_duration(2) for img in images]
        video = concatenate_videoclips(clips, method="compose")

        audio_voice = AudioFileClip(voice_path)
        audio_music = AudioFileClip(music_path).volumex(0.3)
        audio_final = CompositeAudioClip([audio_voice, audio_music])

        video = video.set_audio(audio_final)
        video = video.set_duration(audio_voice.duration)

        filename = f"{job_id}.mp4"
        output_path = os.path.join("videos", filename)
        os.makedirs("videos", exist_ok=True)
        video.write_videofile(output_path, fps=24)

        send_discord_message(f"✅ Job {job_id} terminé ! Vidéo générée.")
        send_discord_message(f"📹 Lien Dropbox (à uploader manuellement ou automatiquement) : `{filename}`")

    except Exception as e:
        send_discord_message(f"❌ Job {job_id} a échoué : {str(e)}")

@app.route("/start-job", methods=["POST"])
def start_job():
    job_id = str(uuid.uuid4())

    files = request.files
    subtitle_text = request.form.get("subtitle")

    if not files or not subtitle_text:
        return jsonify({"error": "Fichiers ou sous-titres manquants"}), 400

    images = []
    for i in range(5):
        img = files.get(f"image{i+1}")
        if img:
            path = f"temp/{job_id}_img{i+1}.jpg"
            os.makedirs("temp", exist_ok=True)
            img.save(path)
            images.append(path)

    voice = files.get("voice")
    music = files.get("music")

    voice_path = f"temp/{job_id}_voice.mp3"
    music_path = f"temp/{job_id}_music.mp3"
    voice.save(voice_path)
    music.save(music_path)

    thread = Thread(target=generate_video, args=(job_id, images, voice_path, music_path, subtitle_text))
    thread.start()

    return jsonify({"job_id": job_id, "status": "processing"}), 200

@app.route("/", methods=["GET"])
def health():
    return "🚀 Zap Insolite Server is online!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
