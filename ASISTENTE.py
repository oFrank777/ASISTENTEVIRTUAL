import speech_recognition as sr
import pyttsx3
import time
import sys
import tkinter as tk
import random
import json
from tkinter import messagebox
from PIL import Image, ImageTk

recognizer = sr.Recognizer()
microphone = sr.Microphone()
salir = False

def texto_a_audio(comando):
    palabra = pyttsx3.init()
    palabra.say(comando)
    palabra.runAndWait()

def capturar_voz(reconocer, microfono, tiempo_ruido = 0.7):
    if not isinstance(reconocer, sr.Recognizer):
        raise TypeError("'reconocer' no es de la instacia 'Recognizer'")

    if not isinstance(microfono, sr.Microphone):
        raise TypeError("'reconocer' no es de la instacia 'Recognizer'")
    
    with microfono as fuente:
        reconocer.adjust_for_ambient_noise(fuente, duration = tiempo_ruido)
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
        respuesta["error"] = "Habla inteligible"
    return respuesta

def enviar_voz():
    while (1):
        palabra = capturar_voz(recognizer, microphone)
        if palabra["mensaje"]:
            break
        if not palabra["suceso"]:
            print("Algo no está bien. No puedo reconocer tu micrófono o no lo tienes enchufado. <", nombre["error"],">")
            texto_a_audio("Algo no está bien. No puedo reconocer tu micrófono o no lo tienes enchufado.")
            exit(1)
        print("No pude escucharte, ¿podrias repetirlo?\n")
        texto_a_audio("No pude escucharte, ¿podrias repetirlo?")
    return palabra["mensaje"].lower()

with open('basedatos.json', 'r') as archivo:
    datos = json.load(archivo)

if __name__ == "__main__":

    root = tk.Tk()
    root.iconbitmap("IMG/icon.ico") 

    root.geometry("800x600") 
    root.title("ASISTENTE VIRTUAL")

    # Espacio para imagen 
    image = Image.open("IMG/iaBackground.jpg")
    image = image.resize((790, 450))
    img = ImageTk.PhotoImage(image)

    lbl_image = tk.Label(root, image=img)
    lbl_image.grid(column=0, row=0, pady=20)  # Añadido pady para espacio vertical

    text = "Haz click en el boton 'iniciar' para empezar"

    lbl_text = tk.Label(root, text=text, font=("Arial", 16, "bold"))
    lbl_text.grid(column=0, row=1)


    # Botón inicio
    def start():
        print("running assistant ... :V")
        
        #USANDO LA FUNCION TEXTO_A_AUDIO SE HACE LEER CADENAS DE TEXTO, COMO SI LA COMPUTADORA TE ESTUVIERA HABLANDO
        lbl_text.config(text="Bienvenid@")

        texto_a_audio(datos['bienvenida'])
        
        lbl_text.config(text="Tu nombre: ")
        
        nombre = enviar_voz()
        
        lbl_text.config(text="Hola "+nombre)
        texto_a_audio("Hola {}. Mucho gusto.".format(nombre))
        texto_a_audio("{} Ahora voy a explicarte sobre las opciones que tiene este programa. Tienes 3 opciones para escoger.".format(nombre))
        lbl_text.config(text="1) Aprendizaje   2) Tests    3) Juegos")
        texto_a_audio("Aprendizaje. Tests. Juegos.")
        texto_a_audio("La opción Aprendizaje es donde podrás aprender todo con respecto a Programacion. La opción Tests es donde podrás poner en práctica lo que aprendiste mediante preguntas. Y por último, la tercer opción, es Juegos, donde tambien podrás poner en accion lo que aprendiste jugando.")
        texto_a_audio("¿Qué opción eliges?")
        time.sleep(0.5)
        texto_a_audio("¿Aprendizaje? ¿Tests? ¿Juegos?")
        
        #SE USA LA FUNCION SLEEP DE LA LIBRERIA TIME PARA PAUSAR UN TIEMPO LA EJECUCION DEL PROGRAMA
        #PARA QUE LA INTERACCION SEA MAS NATURAL
        time.sleep(0.5)


    btn_start = tk.Button(root, text="Iniciar", command=start, font=("Arial", 12, "bold"))  # Cambiado el tamaño de la fuente
    btn_start.grid(column=0, row=2, pady=10)  # Añadido pady para espacio vertical

    root.mainloop()