from flask import Flask, request, jsonify
from moviepy.editor import *
import os
import datetime

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "🚀 Zap Insolite API est active !"

@app.route("/assemble", methods=["POST"])
def assemble_video():
    try:
        files = request.files
        required_files = ['voice', 'music'] + [f'image{i}' for i in range(1, 6)]

        for name in required_files:
            if name not in files:
                return jsonify({"error": f"Missing file: {name}"}), 400

        # Créer le dossier output s'il n'existe pas
        os.makedirs("output", exist_ok=True)

        # Sauvegarder tous les fichiers
        voice_path = "voice.mp3"
        music_path = "music.mp3"
        image_paths = []

        files['voice'].save(voice_path)
        files['music'].save(music_path)

        for i in range(1, 6):
            img_path = f"image{i}.jpg"
            files[f'image{i}'].save(img_path)
            image_paths.append(img_path)

        # Création des clips image
        clips = [ImageClip(img).set_duration(2) for img in image_paths]
        video = concatenate_videoclips(clips, method="compose")

        # Ajouter la voix
        voice = AudioFileClip(voice_path)
        music = AudioFileClip(music_path).volumex(0.2)

        # Mix audio
        final_audio = CompositeAudioClip([music, voice])
        final_audio = final_audio.set_duration(video.duration)

        video = video.set_audio(final_audio)

        # Nom unique pour la vidéo
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"output/video_{timestamp}.mp4"
        video.write_videofile(output_path, fps=24)

        return jsonify({"status": "success", "video_path": output_path})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
