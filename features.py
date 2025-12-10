import os
import requests
from datetime import datetime
import re
import sqlite3
import webbrowser
import threading
import time
import pandas as pd
import numpy as np
import pywhatkit as kit
import wikipedia
import pygame

try:
    from pydub import AudioSegment
    from pydub.playback import play
except ImportError:
    print("Warning: 'pydub' is not installed. Sound functions may fail.")
    # Define placeholder functions if pydub is missing to prevent crashes
    def play(*args, **kwargs): pass
    def AudioSegment(*args, **kwargs): return None

# Data Science Imports
from collections import Counter
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LinearRegression

# Translation Import
try:
    from deep_translator import GoogleTranslator
except ImportError:
    print("Warning: 'deep_translator' is not installed. Translation function will fail.")
    class GoogleTranslator:
        def __init__(self, *args, **kwargs): pass
        def translate(self, text): return f"Translation function unavailable for: {text}"

# COMMAND/SPEAK FUNCTION (MUST BE PROVIDED)
from engine.command import speak 

from wikipedia.exceptions import DisambiguationError, PageError


import eel 


ASSISTANT_NAME = 'man'
WEATHER_API_KEY = "21de39bde37f6b6fe55ccac19a829edb"
CURRENCY_API_KEY = "141b0b2e643c26e9d558a1df"
BASE_URL = f"https://v6.exchangerate-api.com/v6/{CURRENCY_API_KEY}/latest/"

# Connect to SQLite database
conn = sqlite3.connect("man.db")
cursor = conn.cursor()


@eel.expose
def playClickSound():
    # Use the pydub path (os.path.join is cross-platform safe)
    sound_file_pydub = os.path.join('www', 'assets', 'audio', 'click_sound.mp3') 
    
    def play_sound_thread():
        try:
            # Check if AudioSegment is a real function (i.e., pydub imported successfully)
            if 'AudioSegment' in globals() and not isinstance(AudioSegment(), type(None)): 
                song = AudioSegment.from_file(sound_file_pydub)
                play(song)
        except Exception as e:
            pass # Fails silently
            
    threading.Thread(target=play_sound_thread).start()

# Play startup sound (ONLY uses pydub)
def playAssistantSound():
    sound_file_pydub = os.path.join('www', 'assets', 'audio', 'start_sound.mp3') 
            
    def play_sound_thread():
        try:
            if 'AudioSegment' in globals() and not isinstance(AudioSegment(), type(None)): 
                song = AudioSegment.from_file(sound_file_pydub)
                play(song)
        except Exception:
            pass # Fails silently
            
    threading.Thread(target=play_sound_thread).start()


# Play alarm sound (ONLY uses pydub)
def playAlarmSound():
    music_dir = os.path.join('www', 'assets', 'audio', 'alarm.wav')
    
    def play_alarm_thread():
        try:
            if 'AudioSegment' in globals() and not isinstance(AudioSegment(), type(None)): 
                song = AudioSegment.from_file(music_dir)
                play(song)
        except Exception:
            pass # Fails silently
            
    threading.Thread(target=play_alarm_thread).start()


def playTimerSound(duration):
    # This function uses the pygame library
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        path = os.path.join("www", "assets", "audio", "timer.mp3")
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1)  # Loop the sound indefinitely
        time.sleep(duration)
        pygame.mixer.music.stop()
    except Exception as e:
        pass 


# --- CORE COMMAND FUNCTIONS (No changes needed) ---

def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "").strip().lower()

    if query:
        try:
            cursor.execute('SELECT path FROM sys_command WHERE LOWER(name) = ?', (query,))
            results = cursor.fetchall()
            if results:
                speak("Opening " + query)
                os.startfile(results[0][0])
                return

            cursor.execute('SELECT url FROM web_command WHERE LOWER(name) = ?', (query,))
            results = cursor.fetchall()
            if results:
                speak("Opening " + query)
                webbrowser.open(results[0][0])
                return

            speak("Opening " + query)
            os.system('start ' + query)
        except Exception as e:
            speak(f"Something went wrong: {str(e)}")

def searchWikipedia(query):
    query = query.lower()
    for phrase in ['search', 'about', 'who is', 'what is', 'tell me about']:
        query = query.replace(phrase, '')
    query = query.strip()

    try:
        summary = wikipedia.summary(query, sentences=4)
        if len(summary) < 50:
            page = wikipedia.page(query)
            first_paragraph = page.content.split('\n\n')[0] 
            summary = first_paragraph if len(first_paragraph) > 0 else summary

        speak(f"According to Wikipedia, {summary}")
        return summary
    except DisambiguationError as e:
        speak(f"Your query is ambiguous. Did you mean: {e.options[0]}?")
        return e.options[0]
    except PageError:
        speak("Sorry, I couldn't find any information on that topic.")
        return ""
    except Exception as e:
        speak("An error occurred while searching Wikipedia.")
        return ""

def extract_yt_term(command):
    pattern = r'play\s+(.*?)(?:\s+on\s+youtube)?$'
    match = re.search(pattern, command, re.IGNORECASE)
    return match.group(1).strip() if match else None

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    if search_term:
        speak("Playing " + search_term + " on YouTube")
        kit.playonyt(search_term)
    else:
        speak("Sorry, I couldn't find what to play on YouTube.")

def tellDateTime():
    now = datetime.now()
    date = now.strftime("%A, %d %B %Y")
    current_time = now.strftime("%I:%M %p")
    speak(f"Today is {date} and the time is {current_time}")
    return f"{date}, {current_time}"

def getWeather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        if data["cod"] != 200:
            speak("Sorry, I couldn't find the weather for that location.")
            return "Weather data not found."

        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        weather_info = f"The temperature in {city} is {temp} degrees Celsius with {desc}."
        speak(weather_info)
        return weather_info
    except Exception:
        speak("Something went wrong while fetching the weather.")
        return "Error fetching weather."

def analyzeAndPredictCSV_live(file_name, model_name="knn"):
    try:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        csv_path = os.path.join(desktop, file_name)
        
        if not os.path.exists(csv_path):
            speak(f"Sorry, I could not find {file_name} on your desktop.")
            return
        df = pd.read_csv(csv_path)

        speak(f"The dataset has {df.shape[0]} rows and {df.shape[1]} columns.")
        columns = df.columns.tolist()
        speak("The dataset contains the following columns:")
        for col in columns:
            speak(col)

        if df.isnull().sum().sum() > 0:
            speak("Filling missing values with zeros.")
            df = df.fillna(0)

        df_numerical = df.select_dtypes(include=['number'])
        numerical_columns = df_numerical.columns.tolist()

        if not numerical_columns:
            speak("There are no numerical columns in this dataset. Cannot run model.")
            return

        speak("The numerical fields are:")
        for col in numerical_columns:
            speak(col)

        X = df_numerical.iloc[:, :-1]
        y = df_numerical.iloc[:, -1]
        
        if X.empty or y.empty or len(X) != len(y):
            speak("Data preparation failed. Check your CSV structure.")
            return

        model_name = model_name.lower()

        if model_name == "knn":
            model = KNeighborsClassifier(n_neighbors=3)
            speak("Training K-Nearest Neighbors model now.")
            model.fit(X, y)
            predictions = model.predict(X)
            prediction_counts = Counter(predictions)
            speak("Prediction summary:")
            for label, count in prediction_counts.items():
                speak(f"{label}: {count} instances.")

        elif model_name == "naive bayes":
            model = GaussianNB()
            speak("Training Naive Bayes model now.")
            model.fit(X, y)
            predictions = model.predict(X)
            prediction_counts = Counter(predictions)
            speak("Prediction summary:")
            for label, count in prediction_counts.items():
                speak(f"{label}: {count} instances.")

        elif model_name == "linear regression":
            model = LinearRegression()
            speak("Training Linear Regression model now.")
            model.fit(X, y)
            predictions = model.predict(X)
            mean_pred = np.mean(predictions)
            min_pred = np.min(predictions)
            max_pred = np.max(predictions)
            speak(f"The predictions range from {min_pred:.2f} to {max_pred:.2f} with an average of {mean_pred:.2f}.")

        else:
            speak(f"Model {model_name} is not supported.")
            return

    except Exception as e:
        speak(f"An error occurred during data analysis: {str(e)}")

def convert_currency(amount, from_currency, to_currency):
    try:
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        response = requests.get(BASE_URL + from_currency)
        data = response.json()

        if data['result'] == 'success':
            rates = data['conversion_rates']
            if to_currency in rates:
                converted_amount = amount * rates[to_currency]
                speak(f"{amount} {from_currency} is approximately {converted_amount:.2f} {to_currency}.")
                return converted_amount
            else:
                speak(f"Currency {to_currency} not supported.")
        else:
            speak("Failed to retrieve currency data.")
    except Exception as e:
        speak(f"Error in currency conversion: {str(e)}")

def sendWhatsAppMessage(name, message):
    contact_mapping = {
        "aiman": "+923332059639",
        "mustafa": "+923323705164",
        "nazish": "+923340252187"
    }

    number = contact_mapping.get(name.lower())
    if not number:
        speak(f"I couldn't find the number for {name}. Please check your contact list.")
        return

    now = datetime.now() 
    send_hour = now.hour
    send_minute = now.minute + 2  

    if send_minute >= 60:
        send_minute -= 60
        send_hour = (send_hour + 1) % 24 

    speak(f"Sending WhatsApp message to {name}")
    kit.sendwhatmsg(number, message, send_hour, send_minute, wait_time=20)


def set_timer(seconds):
    def timer_job():
        speak(f"Timer started for {seconds} seconds")
        playTimerSound(seconds)
        speak("Time's up!")

    threading.Thread(target=timer_job).start()

def translate_text(text, target_language):
    try:
        translated = GoogleTranslator(source='auto', target=target_language).translate(text)
        result = f"{text} in {target_language} is {translated}"
        speak(result)
        return result
    except Exception as e:
        speak("Translation failed.")
        print(str(e))

def small_talk_responses(query):
    query = query.lower().strip()
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
    how_are_you = ['how are you', 'how are you doing', "whats up", 'how is it going']

    if query in greetings:
        return "Hello! How can I help you today?"
    if any(phrase in query for phrase in how_are_you):
        return "I'm doing great, thanks for asking! How about you?"
    if "who created you" in query or "who made you" in query:
        return "I was made by Aiman Mustafa and Naveen."
    if query in ['bye', 'goodbye', 'see you']:
        return "Goodbye! Have a great day!"
    return None

import re

import requests 
@eel.expose
def allCommands(command=None):
    """
    Central function to process either voice input (via take_command)
    or typed input (via the 'command' argument).
    """
    
    if not command:
        try:
            # FIX: LOCAL IMPORT to break the circular dependency loop
            from engine.command import take_command
            speak("Listening...")
            query = take_command() # Calls the renamed function
            speak(f"You said: {query}")
        except ImportError:
            speak("Microphone input is not configured.")
            return
        
    # 2. Handle Typed Input
    else:
        query = command
        speak(f"You typed: {query}")

    # --- VOICE/TEXT PROCESSING LOGIC STARTS HERE ---
    
    if not query:
        speak("I didn't catch that.")
        eel.ShowHood()
        return

    print(f"Command received: {query}")
    query = query.lower().strip()
    
    try:
        # --- Small Talk (Highest Priority) ---
        small_talk_reply = small_talk_responses(query)
        if small_talk_reply:
            speak(small_talk_reply)
            eel.DisplayMessage(small_talk_reply) 
            eel.ShowHood()
            return
            
        # --- Other Functional Commands ---
        
        if 'open' in query:
            openCommand(query)

        elif 'play' in query and 'youtube' in query:
            PlayYoutube(query)

        elif any(keyword in query for keyword in ['search', 'about', 'who is', 'what is', 'tell me about']):
            searchWikipedia(query)

        elif ("time" in query or "date" in query or "day" in query ) and not "timer" in query :
            tellDateTime()

        elif "weather" in query or "temperature" in query:
            # Re-implemented the detailed weather logic
            
            city_match = re.search(r'in\s+([a-zA-Z\s]+)', query)
            
            if city_match:
                city = city_match.group(1).strip()
                getWeather(city)
            else:
                try:
                    # Uses the globally imported 'requests' library
                    ip_info = requests.get("https://ipinfo.io").json()
                    city = ip_info.get("city")
                    if city:
                        speak(f"Showing weather for your current location: {city}")
                        getWeather(city)
                    else:
                        speak("Couldn't detect your current city. Please specify it.")
                except Exception as e:
                        speak("There was a problem detecting your location.")

        elif "analyze" in query and ".csv" in query:
            file_match = re.search(r"(\w+\.csv)", query)
            if file_match:
                file_name = file_match.group(1)
                # Note: No need for internal feature imports since all features are in this file
                if "naive bayes" in query:
                    analyzeAndPredictCSV_live(file_name, model_name="naive bayes")
                elif "linear regression" in query:
                    analyzeAndPredictCSV_live(file_name, model_name="linear regression")
                elif "knn" in query:
                    analyzeAndPredictCSV_live(file_name, model_name="knn")
                else:
                    analyzeAndPredictCSV_live(file_name)
            else:
                speak("Please specify the CSV file name.")

        elif "convert" in query:
            currency_match = re.search(r'convert\s+(\d+\.?\d*)\s+(\w+)\s+to\s+(\w+)', query)
            if currency_match:
                amount = float(currency_match.group(1))
                from_curr = currency_match.group(2)
                to_curr = currency_match.group(3)
                convert_currency(amount, from_curr, to_curr)
            else:
                speak("Please say like 'convert 10 USD to EUR'.")
        
        elif "set timer" in query:
            match = re.search(r'set timer for (\d+)\s*(seconds|minutes)', query)
            if match:
                amount = int(match.group(1))
                unit = match.group(2)
                seconds = amount * 60 if unit == 'minutes' else amount
                set_timer(seconds)
            else:
                speak("Please say like 'set timer for 2 minutes'")

        elif "message" in query:
            match = re.search(r'message\s+(\w+)\s+(.+)', query)
            if match:
                name = match.group(1)
                msg = match.group(2)
                sendWhatsAppMessage(name, msg)
            else:
                speak("Please specify the contact and message.")

        elif "translate" in query:
            match = re.search(r'translate (.+) in (\w+)', query)
            if match:
                text = match.group(1)
                language = match.group(2)
                translate_text(text, language)
            else:
                speak("Please say like 'translate hello in french'.")
                
        else:
            speak("Sorry, I couldn't understand.")
            

    except Exception as e:
        speak(f"An error occurred: {str(e)}")

    eel.ShowHood()