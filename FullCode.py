import sounddevice as sd
import vosk
import queue
import json
import arabic_reshaper
from bidi.algorithm import get_display
import cohere
from gtts import gTTS
import pygame
import os

# Cohere
co = cohere.Client("HERE") #Put Your API KEY Here

# Vosk
model = vosk.Model("MODELPATH")  # Model File

# Mic Setup
q = queue.Queue()
def callback(indata, frames, time, status):
    q.put(bytes(indata))


def speak(text):
    tts = gTTS(text=text, lang='ar')
    tts.save("reply.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("reply.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue
    pygame.mixer.quit()
    os.remove("reply.mp3")


def get_ai_reply(user_input):
    response = co.chat(
        model="command-r-plus",  
        message=f"رد بالعربية على: {user_input}"
    )
    return response.text.strip()

with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                       channels=1, callback=callback):
    print("🎤 Speak now... (Ctrl+C to stop)")
    rec = vosk.KaldiRecognizer(model, 16000)

    while True:
        try:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                user_text = result.get("text", "").strip()

                if user_text:
                    reshaped_input = arabic_reshaper.reshape(user_text)
                    print("You said:", get_display(reshaped_input))

                    reply = get_ai_reply(user_text)
                    reshaped_reply = arabic_reshaper.reshape(reply)
                    print("AI reply:", get_display(reshaped_reply))

                    speak(reply)

        except KeyboardInterrupt:
            print("\n Session ended.")
            break
