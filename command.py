import re
import time
import pyttsx3
import speech_recognition as sr
import eel
import requests

def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 170)
    eel.DisplayMessage(text)
    engine.say(text)
    engine.runAndWait()

@eel.expose
def take_Command():
    r = sr.Recognizer()
    eel.DisplayMessage('')
    with sr.Microphone() as source:
        print('Listening...')
        eel.DisplayMessage('Listening...')
        r.pause_threshold = 1.2
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, timeout=10, phrase_time_limit=15)
    
    try:
        print('Recognizing...')
        eel.DisplayMessage('Recognizing...')
        query = r.recognize_google(audio, language='en')
        print(f'User said: {query}')
        time.sleep(2)
        eel.DisplayMessage(query)

    except Exception as e:
        return ""
    
    return query.lower()

# @eel.expose
# def allCommands(command=None):
#     # If no command is passed, take voice input
#     if not command:
#         query = take_Command()
#     else:
#         query = command

#     if not query:
#         speak("I didn't catch that.")
#         eel.ShowHood()
#         return

#     print(f"Command received: {query}")
#     query = query.lower().strip()

#     from engine.features import small_talk_responses

#     response = small_talk_responses(query)
#     if response:
#         speak(response)
#         eel.DisplayMessage(response)
#         eel.ShowHood()
#         return
    
#     try:
        
#         if 'open' in query:
#             from engine.features import openCommand
#             openCommand(query)

#         elif 'play' in query and 'youtube' in query:
#             from engine.features import PlayYoutube
#             PlayYoutube(query)

#         elif any(keyword in query for keyword in ['search', 'about', 'who is', 'what is', 'tell me about']):
#             from engine.features import searchWikipedia
#             # Pass your speak function and status_bar widget (or None if not used)
#             result = searchWikipedia(query)

#         elif ("time" in query or "date" in query or "day" in query ) and not "timer" in query :
#             from engine.features import tellDateTime
#             tellDateTime()

#         elif "weather" in query or "temperature" in query:
#             from engine.features import getWeather
    
#             city_match = re.search(r'in\s+([a-zA-Z\s]+)', query)
    
#             if city_match:
#                 city = city_match.group(1).strip()
#                 getWeather(city)
#             else:
#                 # Try to get current city based on IP
#                 try:
#                     ip_info = requests.get("https://ipinfo.io").json()
#                     city = ip_info.get("city")
#                     if city:
#                         speak(f"Showing weather for your current location: {city}")
#                         getWeather(city)
#                     else:
#                         speak("Couldn't detect your current city. Please specify it.")
#                 except Exception as e:
#                         speak("There was a problem detecting your location.")

#         elif "analyze" in query and ".csv" in query:
#             file_match = re.search(r"(\w+\.csv)", query)
#             if file_match:
#                 file_name = file_match.group(1)
#                 if "naive bayes" in query:
#                     from engine.features import analyzeAndPredictCSV_live
#                     analyzeAndPredictCSV_live(file_name, model_name="naive bayes")
#                 elif "linear regression" in query:
#                     from engine.features import analyzeAndPredictCSV_live
#                     analyzeAndPredictCSV_live(file_name, model_name="linear regression")
#                 elif "knn" in query:
#                     from engine.features import analyzeAndPredictCSV_live
#                     analyzeAndPredictCSV_live(file_name, model_name="knn")
#                 else:
#                     from engine.features import analyzeAndPredictCSV_live
#                     analyzeAndPredictCSV_live(file_name)
#             else:
#                 speak("Please specify the CSV file name.")

#         elif "convert" in query:
#             # Currency conversion
#             currency_match = re.search(r'convert\s+(\d+\.?\d*)\s+(\w+)\s+to\s+(\w+)', query)
#             if currency_match:
#                 amount = float(currency_match.group(1))
#                 from_curr = currency_match.group(2)
#                 to_curr = currency_match.group(3)
#                 from engine.features import convert_currency
#                 convert_currency(amount, from_curr, to_curr)
        
#         elif "set timer" in query:
 
#             match = re.search(r'set timer for (\d+)\s*(seconds|minutes)', query)
#             if match:
#                 amount = int(match.group(1))
#                 unit = match.group(2)
#                 seconds = amount * 60 if unit == 'minutes' else amount
#                 from engine.features import set_timer
#                 set_timer(seconds)
#             else:
#                 speak("Please say like 'set timer for 2 minutes'")

#         elif "message" in query:
#             match = re.search(r'message\s+(\w+)\s+(.+)', query)
#             if match:
#                 name = match.group(1)
#                 msg = match.group(2)
#                 from engine.features import sendWhatsAppMessage
#                 sendWhatsAppMessage(name, msg)
#             else:
#                 speak("Please specify the contact and message.")

#         elif "translate" in query:
#             from engine.features import translate_text
#             match = re.search(r'translate (.+) in (\w+)', query)
#             if match:
#                 text = match.group(1)
#                 language = match.group(2)
#                 translate_text(text, language)
#             else:
#                 speak("Please say like 'translate hello in french'.")
#         else:
#             speak("Sorry, I couldn't understand.")
            

#     except Exception as e:
#         speak(f"An error occurred: {str(e)}")

#     eel.ShowHood()

