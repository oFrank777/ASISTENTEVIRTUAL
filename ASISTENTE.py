import speech_recognition as sr
import pyttsx3
import tkinter as tk
from PIL import Image, ImageTk
import threading
import queue
import json

recognizer = sr.Recognizer()
microphone = sr.Microphone()
engine = pyttsx3.init()

root = tk.Tk()
root.iconbitmap("IMG/icon.ico")
root.geometry("800x600")
root.title("ASISTENTE VIRTUAL")

# Initialize images/widgets globally
image_queue = queue.Queue()

image = Image.open("IMG/iaBackground.jpg")
image = image.resize((790, 450))
photo = ImageTk.PhotoImage(image)
image_label = tk.Label(root, image = photo)
image_label.grid(column=0, row=0, pady=20)
image_queue.put(photo)

lbl_text = tk.Label(root, text="Haz click en el boton 'iniciar' para empezar", font=("Arial", 13, "bold"))
lbl_text.grid(column=0, row=1)

# Queue for communication between threads
queue_ui_to_main = queue.Queue()
queue_main_to_ui = queue.Queue()

with open('basedatos.json', 'r') as archivo:
    datos = json.load(archivo)

def texto_a_audio(text):
    engine.say(text)
    engine.runAndWait()

def capturar_voz(reconocer, microfono, tiempo_ruido=0.5):
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

# def enviar_image(ruta):
#    image = Image.open("" + ruta)
#    image = image.resize((790, 450))
#    photo = ImageTk.PhotoImage(image)
#    image_queue.put(photo)

def execute_start_logic():
    send_text_to_ui("Bienvenid@")
    texto_a_audio("Bienvenido")
    send_text_to_ui("¿Comó te llamas?")
    texto_a_audio("¿Comó te llamas?")
    nombre = "w"
    send_text_to_ui("Hola " + nombre)
    texto_a_audio("Hola {}. Mucho gusto.".format(nombre))
    texto_a_audio(datos["bienvenida"])
    texto_a_audio(
        "{} ahora voy a explicarte sobre las opciones que tiene este programa. Tienes 3 opciones para escoger.".format(
            nombre))
    send_text_to_ui("1) Aprendizaje   2) Tests    3) Juegos")
    texto_a_audio("Aprendizaje. Tests. Juegos.")
    texto_a_audio(
        "La opción Aprendizaje es donde podrás aprender todo con respecto a Programación. La opción Tests es donde podrás poner en práctica lo que aprendiste mediante preguntas. Y por último, la tercer opción, es Juegos, donde también podrás poner en acción lo que aprendiste jugando.")
    send_text_to_ui("¿Qué opción eliges?")
      
    respuesta = "aprendizaje"

    if respuesta == "aprendizaje":

        #enviar_image("IMG/computador.jpg")
        image = Image.open("IMG/computador.jpg")
        image = image.resize((790, 450))
        photo = ImageTk.PhotoImage(image)
        image_queue.put(photo)

        send_text_to_ui("Elegiste la opcion APRENDIZAJE.")
        texto_a_audio("Elegiste la opcion APRENDIZAJE.")
        texto_a_audio("Muy bien antes de empezar quisiera hacer una introduccion a el tema conocido como Programación.")
        send_text_to_ui("Definicion de PROGRAMACION.")
        texto_a_audio(datos['definicion'])
        send_text_to_ui("IMPORTANCIA.")
        texto_a_audio(datos['importancia'])
        send_text_to_ui("RAZONES.")
        texto_a_audio(datos['razones'])
        texto_a_audio("Como se puede apreciar en la imagen, la Programación contiene varios aspectos y caracteristicas importantes, tales como:")
        texto_a_audio("Variables. Constantes. Tipos de datos. Operadores. Estructuras condicionales. Bucles. Funciones. Compiladores. Depuración. Algoritmos. Estructuras de datos. Programación Orientada a Objetos (POO).")
        
        respuesta = "estructuras de datos"

        if respuesta == "variables":
            texto_a_audio(datos['variables'])
        elif respuesta == "constantes":
            texto_a_audio(datos['constantes'])
        elif respuesta == "tipos de datos":
            texto_a_audio(datos['tipos_de_datos'])
        elif respuesta == "operadores":
            texto_a_audio(datos['operadores'])
        elif respuesta == "estructuras condicionales":
            texto_a_audio(datos['estructuras_condicionales'])
        elif respuesta == "bucles":
            texto_a_audio(datos['bucles'])
        elif respuesta == "funciones":
            texto_a_audio(datos['funciones'])
        elif respuesta == "compiladores":
            texto_a_audio(datos['compiladores'])
        elif respuesta == "depuracion":
            texto_a_audio(datos['depuracion'])
        elif respuesta == "algoritmos":
            texto_a_audio(datos['algoritmos'])
        elif respuesta == "estructuras de datos":
            texto_a_audio(datos['estructuras_de_datos']['definicion'])
            texto_a_audio("existen distintos tipos de estructura, aqui te mostrare 5 de ellas.")
            send_text_to_ui("1) Arrays 2) Listas enlazadas 3) Pilas 4) Colas 5) Hash\n¿Por cual deseas empezar?")
            texto_a_audio("¿Por cual deseas empezar?")
        

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
        pass
    
    try:
        photo = image_queue.get_nowait()     
        image_label.config(image = photo)        


    except queue.Empty: 
        pass
        
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
