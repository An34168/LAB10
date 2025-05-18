import json
import requests
import pyttsx3
import queue
import sounddevice as sd
import vosk
import os
import datetime

# Inicialización
engine = pyttsx3.init()
model = vosk.Model("model")  # Asegúrate de tener la carpeta del modelo
q = queue.Queue()

def speak(text):
    print("Ассистент:", text)
    engine.say(text)
    engine.runAndWait()

# ✅ Escuchar desde el micrófono
def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

def listen():
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        rec = vosk.KaldiRecognizer(model, 16000)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                return result.get("text", "")


# Funciones API
def get_holidays():
    url = "https://date.nager.at/api/v3/PublicHolidays/2024/GB"
    response = requests.get(url)
    return response.json()

def listar_nombres(holidays):
    return [h['localName'] for h in holidays]

def guardar_en_archivo(holidays):
    with open("feriados.txt", "w", encoding="utf-8") as f:
        for h in holidays:
            f.write(f"{h['date']} - {h['localName']}\n")
    speak("Файл сохранён.")

def listar_fechas_nombres(holidays):
    for h in holidays:
        speak(f"{h['date']}: {h['localName']}")

def feriado_mas_cercano(holidays):
    hoy = datetime.date.today()
    futuros = [h for h in holidays if datetime.date.fromisoformat(h['date']) >= hoy]
    if futuros:
        primero = futuros[0]
        speak(f"Ближайший праздник: {primero['localName']} - {primero['date']}")
    else:
        speak("Ближайших праздников нет.")

def contar(holidays):
    speak(f"Всего праздников: {len(holidays)}")

# Main loop
def main():
    speak("Голосовой ассистент запущен.")
    holidays = get_holidays()
    while True:
        speak("Слушаю команду...")
        texto = listen()
        if not texto:
            continue

        if "перечислить" in texto:
            nombres = listar_nombres(holidays)
            for nombre in nombres:
                speak(nombre)
        elif "сохранить" in texto:
            guardar_en_archivo(holidays)
        elif "даты" in texto:
            listar_fechas_nombres(holidays)
        elif "ближайший" in texto:
            feriado_mas_cercano(holidays)
        elif "количество" in texto:
            contar(holidays)
        elif "стоп" in texto or "выход" in texto:
            speak("До свидания!")
            break
        else:
            speak("Команда не распознана.")

if __name__ == "__main__":
    main()

