import speech_recognition as sr
import pyttsx3
import tkinter as tk
from PIL import Image, ImageTk
import threading
import queue

recognizer = sr.Recognizer()
microphone = sr.Microphone()
engine = pyttsx3.init()

root = tk.Tk()
root.iconbitmap("IMG/icon.ico")
root.geometry("800x600")
root.title("ASISTENTE VIRTUAL")

# Initialize images/widgets globally
image = Image.open("IMG/iaBackground.jpg")
image = image.resize((790, 450))
img = ImageTk.PhotoImage(image)

lbl_image = tk.Label(root, image=img)
lbl_image.grid(column=0, row=0, pady=20)

lbl_text = tk.Label(root, text="Haz click en el boton 'iniciar' para empezar", font=("Arial", 16, "bold"))
lbl_text.grid(column=0, row=1)

# Queue for communication between threads
queue_ui_to_main = queue.Queue()
queue_main_to_ui = queue.Queue()

def texto_a_audio(text):
    engine.say(text)
    engine.runAndWait()

def capturar_voz(reconocer, microfono, tiempo_ruido=0.7):
    with microfono as fuente:
        reconocer.adjust_for_ambient_noise(fuente, duration=tiempo_ruido)
        print("Escuchando...")
        audio = reconocer.listen(fuente)

    respuesta = {
        "suceso": True,
        "error": None,
        "mensaje": None,
    }
    try:
        respuesta["mensaje"] = reconocer.recognize_google(audio, language="es-PE")
    except sr.RequestError:
        respuesta["suceso"] = False
        respuesta["error"] = "API no disponible"
    except sr.UnknownValueError:
        respuesta["error"] = "Habla ininteligible"
    return respuesta

def main_thread_logic():
    while True:
        command = queue_ui_to_main.get()
        if command == "start":
            execute_start_logic()

def execute_start_logic():
    send_text_to_ui("Bienvenid@")
    texto_a_audio("Bienvenido")
    send_text_to_ui("Tu nombre: ")
    nombre = enviar_voz()
    send_text_to_ui("Hola " + nombre)
    texto_a_audio("Hola {}. Mucho gusto.".format(nombre))
    texto_a_audio(
        "{} Ahora voy a explicarte sobre las opciones que tiene este programa. Tienes 3 opciones para escoger.".format(
            nombre))
    send_text_to_ui("1) Aprendizaje   2) Tests    3) Juegos")
    texto_a_audio("Aprendizaje. Tests. Juegos.")
    texto_a_audio(
        "La opción Aprendizaje es donde podrás aprender todo con respecto a Programación. La opción Tests es donde podrás poner en práctica lo que aprendiste mediante preguntas. Y por último, la tercer opción, es Juegos, donde también podrás poner en acción lo que aprendiste jugando.")
    send_text_to_ui("¿Qué opción eliges?")
    texto_a_audio("¿Aprendizaje? ¿Tests? ¿Juegos?")

def enviar_voz():
    palabra = capturar_voz(recognizer, microphone)
    if not palabra["suceso"]:
        print("Algo no está bien. No puedo reconocer tu micrófono o no lo tienes enchufado. <", palabra["error"], ">")
        texto_a_audio("Algo no está bien. No puedo reconocer tu micrófono o no lo tienes enchufado.")
        exit(1)
    return palabra["mensaje"].lower()

def send_text_to_ui(text):
    queue_main_to_ui.put(text)
    root.after(0, update_ui)

def update_ui():
    try:
        text = queue_main_to_ui.get_nowait()
        lbl_text.config(text=text)
    except queue.Empty:
        root.after(100, update_ui)

def start():
    queue_ui_to_main.put("start")

# Start the main thread
main_thread = threading.Thread(target=main_thread_logic)
main_thread.daemon = True
main_thread.start()

btn_start = tk.Button(root, text="Iniciar", command=start, font=("Arial", 12, "bold"))
btn_start.grid(column=0, row=2, pady=10)

# Run the main loop directly
root.mainloop()
