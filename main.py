from flask import Flask, jsonify
from moviepy.editor import *
import os

app = Flask(__name__)

@app.route("/")
def hello():
    return "🚀 Zap Insolite API est en ligne !"

@app.route("/assemble")
def assemble_video():
    try:
        # Assure-toi que ces fichiers existent dans le dossier assets/
        image = "assets/image.jpg"
        voice = "assets/voice.mp3"
        music = "assets/music.mp3"  # facultatif

        # Clip vidéo à partir d'une image fixe (5s)
        clip = ImageClip(image, duration=5)

        # Audio principal : voix off
        voice_clip = AudioFileClip(voice)

        # Facultatif : musique de fond
        if os.path.exists(music):
            music_clip = AudioFileClip(music).volumex(0.2)
            final_audio = CompositeAudioClip([voice_clip, music_clip])
        else:
            final_audio = voice_clip

        # Appliquer l'audio au clip
        clip = clip.set_audio(final_audio)

        # Sous-titres simples (affichés sur la vidéo)
        subtitles = TextClip("Saviez-vous que les pieuvres ont 3 cœurs ?", fontsize=40, color='white', font='Arial')
        subtitles = subtitles.set_position(("center", "bottom")).set_duration(5)

        # Vidéo finale avec image + texte + audio
        final = CompositeVideoClip([clip, subtitles])

        # Crée le dossier de sortie si pas présent
        os.makedirs("output", exist_ok=True)
        final.write_videofile("output/video.mp4", fps=24)

        return jsonify({"status": "✅ Vidéo générée", "path": "/output/video.mp4"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
