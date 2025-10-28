import tkinter as tk
from tkinter import Scrollbar
from PIL import Image, ImageTk
import datetime
import pyttsx3
import threading
import speech_recognition as sr
import pyjokes
import requests
from bs4 import BeautifulSoup
import pyautogui
import random
from time import sleep
import webbrowser
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from googletrans import Translator

# Initialize text-to-speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# Reminders list
reminders = []

# Health tips list
health_tips = [
    "Drink plenty of water to stay hydrated.",
    "Try to exercise for at least 30 minutes a day.",
    "Eat a balanced diet with plenty of fruits and vegetables.",
    "Get at least 7-8 hours of sleep each night.",
    "Practice mindfulness or meditation to reduce stress."
]

# Quotes list
quotes = [
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Success is not the key to happiness. Happiness is the key to success. - Albert Schweitzer",
    "Believe you can and you're halfway there. - Theodore Roosevelt",
    "It always seems impossible until it's done. - Nelson Mandela"
]

# Spotify API Setup (Replace with your actual credentials)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="your_spotify_client_id",
                                               client_secret="your_spotify_client_secret",
                                               redirect_uri="your_redirect_uri",
                                               scope=["user-library-read", "user-read-playback-state", "user-modify-playback-state"]))

# Function to speak text
def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def process_input(user_input):
    if "translate" in user_input.lower():
        parts = user_input.lower().split()
        try:
            text_to_translate = parts[1]
            target_language = parts[-1]
            translated_text = translate_text(text_to_translate, target_language)
            return f"Translated '{text_to_translate}' to {target_language}: {translated_text}"
        except IndexError:
            return "Sorry, I couldn't understand the translation request. Please specify the text and language."
    
    elif "time" in user_input.lower():
        return f"The current time is {datetime.datetime.now().strftime('%H:%M:%S')}"
    elif "hello" in user_input.lower():
        return "Hello! How can I assist you today?"
    elif "joke" in user_input.lower():
        return pyjokes.get_joke()
    elif "quote" in user_input.lower():
        return random.choice(quotes)
    elif "health tips" in user_input.lower():
        return random.choice(health_tips)
    elif "set a reminder" in user_input.lower():
        speak("What time should I remind you? Please say in HH:MM format.")
        reminder_time = listen_to_voice().strip()
        speak("What should I remind you about?")
        task = listen_to_voice()
        reminders.append({"time": reminder_time, "task": task})
        return f"Reminder set for {reminder_time} to {task}"
    elif "search" in user_input.lower():
        speak("What would you like to search for?")
        search_query = listen_to_voice().strip()
        webbrowser.open(f"https://www.google.com/search?q={search_query}")
        return f"Searching for {search_query} on Google."
    elif "news" in user_input.lower():
        return get_latest_news()
    elif "play music" in user_input.lower():
        return play_music()
    elif "exit" in user_input.lower():
        return "Goodbye! Have a great day!"
    elif "information of weather" in user_input.lower():  
        webbrowser.open(f"https://www.google.com/search?q=weather")
        return "Opening weather information."
    elif "cricket score" in user_input.lower(): 
        webbrowser.open(f"https://www.cricbuzz.com/live-cricket-scorecard")
        return "Opening cricket score information."
    elif "open spotify" in user_input.lower():
        speak("Opening Spotify")
        webbrowser.open("https://open.spotify.com/")
    elif "open google" in user_input.lower():
        speak("Opening Google")
        webbrowser.open("https://www.google.co.in/")
    elif "open youtube" in user_input.lower():
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com/")
    else:
        return "I'm sorry, I didn't understand that. Can you please repeat?"

# Function to translate text
def translate_text(text, target_lang):
    translator = Translator()
    translated = translator.translate(text, dest=target_lang)
    return translated.text

# Function to get the latest news from Google
def get_latest_news():
    search_query = "latest news"
    url = f"https://www.google.com/search?q={search_query}&tbm=nws"
    r = requests.get(url)
    data = BeautifulSoup(r.text, "html.parser")
    
    # Extracting the headlines from Google News
    headlines = []
    for item in data.find_all("h3"):
        headlines.append(item.get_text())

    if headlines:
        news = "\n".join(headlines[:5])  # Get the top 5 news headlines
        return f"Here are the latest news headlines:\n{news}"
    else:
        return "Sorry, I couldn't fetch the latest news at the moment."

# Function to play music using Spotify API
def play_music():
    # You can customize the song or playlist here
    sp.start_playback()
    return "Playing music on Spotify."

# Function to listen to voice commands
def listen_to_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            speak("Listening...")
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
            user_input = recognizer.recognize_google(audio)
            chat_history.insert(tk.END, f"User: {user_input}\n", "user")

            # Process the user input
            bot_response = process_input(user_input)
            chat_history.insert(tk.END, f"Jarvis: {bot_response}\n", "bot")
            speak(bot_response)
            
        except sr.UnknownValueError:
            speak("Sorry, I could not understand that.")
        except sr.RequestError:
            speak("There was an error with the speech recognition service.")
        except Exception as e:
            speak(f"An error occurred: {e}")

# Function to check reminders in background
def check_reminders():
    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        for reminder in reminders:
            if reminder["time"] == now:
                speak(f"Reminder: {reminder['task']}")
                reminders.remove(reminder)
        sleep(30)

# Function to start the assistant
def start_assistant():
    global is_running
    is_running = True
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    exit_button.config(state=tk.NORMAL)
    speak("Assistant started. You can now talk to me.")
    
    # Start the listening in a separate thread for faster response
    listen_thread = threading.Thread(target=listen_to_voice, daemon=True)
    listen_thread.start()

# Function to stop the assistant
def stop_assistant():
    global is_running
    is_running = False
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    exit_button.config(state=tk.NORMAL)
    speak("Assistant stopped.")

# Function to exit the program
def exit_program():
    root.quit()

# Create the main window
root = tk.Tk()
root.title("Jarvis: Personal Chatbot")
root.geometry("500x900")

# Add bot image (ensure the image path is correct)
bot_image_path = r"C:\Users\shrav\OneDrive\Documents\bot_image.jpg"  # image path
try:
    bot_image = Image.open(bot_image_path)
    bot_image = bot_image.resize((100, 100), Image.Resampling.LANCZOS)
    bot_photo = ImageTk.PhotoImage(bot_image)
    image_label = tk.Label(root, image=bot_photo)
    image_label.pack(pady=10)
except FileNotFoundError:
    bot_image_path = "default_image.png"  # Use a fallback image
    print(f"Image not found at {bot_image_path}. Please check the file path.")

# Add chatbot name
title_label = tk.Label(root, text="Jarvis: Personal Chatbot", font=("Arial", 18, "bold"), fg="darkblue")
title_label.pack()

# Add chat history area
chat_frame = tk.Frame(root)
chat_frame.pack(fill=tk.BOTH, expand=True, padx=10)

scrollbar = Scrollbar(chat_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

chat_history = tk.Text(chat_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, bg="lightgray", font=("Arial", 12))
chat_history.pack(fill=tk.BOTH, expand=True)
chat_history.tag_configure("user", foreground="blue", font=("Arial", 12, "bold"))
chat_history.tag_configure("bot", foreground="green", font=("Arial", 12, "italic"))

scrollbar.config(command=chat_history.yview)

# Add control buttons
button_frame = tk.Frame(root)
button_frame.pack(fill=tk.X, pady=10)

start_button = tk.Button(button_frame, text="Start Assistant", command=start_assistant, bg="green", fg="white", font=("Arial", 12))
start_button.pack(side=tk.LEFT, padx=10)

stop_button = tk.Button(button_frame, text="Stop Assistant", command=stop_assistant, bg="red", fg="white", font=("Arial", 12), state=tk.DISABLED)
stop_button.pack(side=tk.LEFT, padx=10)

exit_button = tk.Button(button_frame, text="Exit", command=exit_program, bg="gray", fg="white", font=("Arial", 12))
exit_button.pack(side=tk.LEFT, padx=10)

# Run the reminder checking thread
threading.Thread(target=check_reminders, daemon=True).start()

# Run the main loop
root.mainloop()
