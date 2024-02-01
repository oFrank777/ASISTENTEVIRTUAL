import speech_recognition as sr
import pyttsx3
import tkinter as tk
from PIL import Image, ImageTk
import threading
import queue
import json
import random

recognizer = sr.Recognizer()
microphone = sr.Microphone()
engine = pyttsx3.init()

root = tk.Tk()
root.iconbitmap("IMG/icon.ico")
root.geometry("800x600")
root.title("ASISTENTE VIRTUAL")
root.config(bg="#262626")
root.resizable(False, False) # deshabilita redimensionamiento
root.maxsize(800, 600) # establece tamaño máximo
root.minsize(800, 600)

# Dimensiones del tablero
WIDTH = 400  
HEIGHT = 400

# Tamaño de las celdas 
CELL_SIZE = 25

class Grid:
    def __init__(self, canvas, width, height, cell_size):
        self.canvas = canvas
        self.WIDTH = width
        self.HEIGHT = height
        self.CELL_SIZE = cell_size

        x1, y1 = random.randint(0, 15), random.randint(0, 15)
        x2, y2 = random.randint(0, 15), random.randint(0, 15)
        self.user_cell = (x1, y1)
        self.goal_cell = (x2, y2)

        self.obstacle_cells = []

        for _ in range(90):
            x3, y3 = random.randint(0, 15), random.randint(0, 15)

            if (x3, y3) != (x2, y2) and (x3, y3) != (x1, y1):
                self.obstacle_cells.append((x3, y3))

        self.cells = []
        self.initialize_cells()
        self.draw_cells()
        
    def initialize_cells(self):
        for row in range(20):
            for col in range(20):
                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                fill_color = "white"
                if (row, col) == self.user_cell:
                    fill_color = "green"
                elif (row, col) == self.goal_cell:
                    fill_color = "red"
                elif (row, col) in self.obstacle_cells:
                    fill_color = "black"

                cell = self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color)
                self.cells.append(cell)

    def draw_cells(self):
        for cell_id in self.cells:
            self.canvas.delete(cell_id)  # Borrar celdas antiguas

        self.initialize_cells()

    def move_up(self, evt):
        self.try_move(self.user_cell[0] - 1, self.user_cell[1])

    def move_down(self, evt):
        self.try_move(self.user_cell[0] + 1, self.user_cell[1])

    def move_left(self, evt):
        self.try_move(self.user_cell[0], self.user_cell[1] - 1)

    def move_right(self, evt):
        self.try_move(self.user_cell[0], self.user_cell[1] + 1)

    def try_move(self, row, col):
        if (row >= 0 and row < 20 and col >= 0 and col < 20 and
                (row, col) not in self.obstacle_cells):
            self.user_cell = (row, col)
            self.draw_cells()

# Initialize images/widgets globally
image_queue = queue.Queue()

image = Image.open("IMG/iaBackground.png")
image = image.resize((790, 450))
photo = ImageTk.PhotoImage(image)
image_label = tk.Label(root, image = photo)

print((root.winfo_reqwidth()))
image_label.grid(column=0, row=0, pady=20, padx=((800 - photo.width())/ 2))
image_label.config(bg="#262626")
image_queue.put(photo)

lbl_text = tk.Label(root, text="Haz click en el boton 'iniciar' para empezar", font=("Arial", 13, "bold"))
lbl_text.config(bg="#262626",
                fg="#fefae4", # color mostaza
                font=("Oswald", 20, "bold")) 
lbl_text.grid(column=0, row=1)

# Queue for communication between threads
queue_ui_to_main = queue.Queue()
queue_main_to_ui = queue.Queue()

with open('basedatos.json', encoding="utf-8") as archivo:
    datos = json.load(archivo)

def texto_a_audio(text):
    engine.say(text)
    engine.runAndWait()

def capturar_voz(reconocer, microfono, tiempo_ruido=0.1):
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
    btn_start.grid_forget()  
    texto_a_audio("Bienvenido")
    send_text_to_ui("¿Comó te llamas?")
    texto_a_audio("¿Comó te llamas?")
    mic_label.grid(column=0, row=2, pady=10)
    nombre = enviar_voz()
    mic_label.grid_forget()
    send_text_to_ui("Hola " + nombre)
    texto_a_audio("Hola {}. Mucho gusto.".format(nombre))
    texto_a_audio(datos["bienvenida"])
    texto_a_audio(
        "{} ahora voy a explicarte sobre las opciones que tiene este programa. Tienes 3 opciones para escoger.".format(
            nombre))
    #WHILE PARA REPETIR O CAMBIAR DE OPCIONES
    send_text_to_ui("OPCIONES: 1) Aprendizaje   2) Cuestionario    3) Juegos")
    texto_a_audio("Aprendizaje. Cuestionario. Juegos.")
    texto_a_audio(
        "La opción Aprendizaje es donde podrás aprender todo con respecto a Programación. La opción Cuestionario es donde podrás poner en práctica lo que aprendiste mediante preguntas. Y por último, la tercer opción, es Juegos, donde también podrás poner en acción lo que aprendiste jugando.")
    texto_a_audio("¿Qué opción eliges?")
    send_text_to_ui("¿Qué opción eliges?")

    mic_label.grid(column=0, row=2, pady=10)  
    respuesta = enviar_voz()
    mic_label.grid_forget()

    if respuesta == "aprendizaje":

        image = Image.open("IMG/introduccionProgramacion.png")
        image = image.resize((790, 450))
        photo = ImageTk.PhotoImage(image)
        image_queue.put(photo)

        send_text_to_ui("Elegiste la opcion APRENDIZAJE.")
        texto_a_audio("Elegiste la opcion APRENDIZAJE.")
        texto_a_audio("Muy bien antes de empezar quisiera hacer una introduccion a el tema conocido como Programación.")
        
        image = Image.open("IMG/definicion.png")
        image = image.resize((790, 450))
        photo = ImageTk.PhotoImage(image)
        image_queue.put(photo)
        send_text_to_ui("Definicion de PROGRAMACION.")
        texto_a_audio(datos['definicion'])

        image = Image.open("IMG/importancia.png")
        image = image.resize((790, 450))
        photo = ImageTk.PhotoImage(image)
        image_queue.put(photo)
        send_text_to_ui("IMPORTANCIA.")
        texto_a_audio(datos['importancia'])

        image = Image.open("IMG/razones.png")
        image = image.resize((790, 450))
        photo = ImageTk.PhotoImage(image)
        image_queue.put(photo)
        send_text_to_ui("RAZONES.")
        texto_a_audio(datos['razones'])
        
        image = Image.open("IMG/conceptos.png")
        image = image.resize((790, 450))
        photo = ImageTk.PhotoImage(image)
        image_queue.put(photo)
        texto_a_audio("Como se puede apreciar en la imagen, la Programación contiene varios aspectos y caracteristicas importantes, tales como:")
        send_text_to_ui("Conceptos de Programacion.")
        texto_a_audio("Variables. Constantes. Tipos de datos. Operadores. Estructuras condicionales. Bucles. Funciones. Compiladores. Depuración. Algoritmos. Estructuras de datos. Programación Orientada a Objetos (POO).")
        texto_a_audio("Cual")
        mic_label.grid(column=0, row=2, pady=10)  
        respuesta = enviar_voz()
        mic_label.grid_forget()

        if respuesta == "variables":
            image = Image.open("IMG/variables.png")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            image_queue.put(photo)
            send_text_to_ui("Variables")
            texto_a_audio(datos['variables'])

        elif respuesta == "constantes":
            image = Image.open("IMG/constantes.png")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            image_queue.put(photo)
            send_text_to_ui("Constantes")
            texto_a_audio(datos['constantes'])

        elif respuesta == "tipos de datos":
            image = Image.open("IMG/tiposDatos.png")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            send_text_to_ui("Tipos de Datos")
            image_queue.put(photo)
            texto_a_audio(datos['tipos_de_datos'])

        elif respuesta == "operadores":
            image = Image.open("IMG/operadores.png")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            send_text_to_ui("Operadores")
            image_queue.put(photo)
            texto_a_audio(datos['operadores'])

        elif respuesta == "estructuras condicionales":
            image = Image.open("IMG/estructurasCoondicionales.png")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            send_text_to_ui("Estructuras condicionales")
            image_queue.put(photo)
            texto_a_audio(datos['estructuras_condicionales'])

        elif respuesta == "bucles":
            image = Image.open("IMG/bucles.png")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            send_text_to_ui("Bucles")
            image_queue.put(photo)
            texto_a_audio(datos['bucles'])

        elif respuesta == "funciones":
            image = Image.open("IMG/funciones.png")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            send_text_to_ui("Funciones")
            image_queue.put(photo)
            texto_a_audio(datos['funciones'])

        elif respuesta == "compiladores":
            image = Image.open("IMG/compiladores.png")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            send_text_to_ui("Compiladores")
            image_queue.put(photo)
            texto_a_audio(datos['compiladores'])

        elif respuesta == "depuracion":
            image = Image.open("IMG/depuradores.png")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            send_text_to_ui("Depuracion")
            image_queue.put(photo)
            texto_a_audio(datos['depuracion'])

        elif respuesta == "algoritmos":
            image = Image.open("IMG/algoritmos.png")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            send_text_to_ui("Algoritmos")
            image_queue.put(photo)
            texto_a_audio(datos['algoritmos'])

        elif respuesta == "estructuras de datos":
            image = Image.open("IMG/estructurasDatos.png")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            image_queue.put(photo)
            send_text_to_ui("Estructuras de datos:")
            texto_a_audio(datos['estructuras_de_datos']['definicion'])
            texto_a_audio("existen distintos tipos de estructura, aqui te mostrare 5 de ellas.")
            send_text_to_ui("1) Arreglos 2) Listas enlazadas 3) Pilas 4) Colas 5) Hash\n¿Por cual deseas empezar?")
            texto_a_audio("¿Por cual deseas empezar?")
            
            while True:

                respuesta = enviar_voz()

                if cond(respuesta) == True:
                    break

                if respuesta == "arreglos":
                    image = Image.open("IMG/array.png")
                    image = image.resize((790, 450))
                    photo = ImageTk.PhotoImage(image)
                    image_queue.put(photo)
                    send_text_to_ui("Arrays:")
                    texto_a_audio(datos['estructuras_de_datos']['arreglos']['descripcion'])
                    texto_a_audio("aqui te presentamos ventajas y desventajas de este tipo de estructura. Ventajas:")
                    texto_a_audio(datos['estructuras_de_datos']['arreglos']['ventajas'])
                    texto_a_audio("Desventajas:")
                    texto_a_audio(datos['estructuras_de_datos']['arreglos']['desventajas'])
                
                elif respuesta == "listas enlazadas":
                    image = Image.open("IMG/linkedList.png")
                    image = image.resize((790, 450))
                    photo = ImageTk.PhotoImage(image)
                    image_queue.put(photo)
                    send_text_to_ui("Lista enlazadas:")
                    texto_a_audio(datos['estructuras_de_datos']['listas_enlazadas']['descripcion'])
                    texto_a_audio("aqui te presentamos ventajas y desventajas de este tipo de estructura. Ventajas:")
                    texto_a_audio(datos['estructuras_de_datos']['listas_enlazadas']['ventajas'])
                    texto_a_audio("Desventajas:")
                    texto_a_audio(datos['estructuras_de_datos']['listas_enlazadas']['desventajas'])
                
                elif respuesta == "pilas":
                    image = Image.open("IMG/pila.png")
                    image = image.resize((790, 450))
                    photo = ImageTk.PhotoImage(image)
                    image_queue.put(photo)
                    send_text_to_ui("Pilas:")
                    texto_a_audio(datos['estructuras_de_datos']['pilas']['descripcion'])
                    texto_a_audio("aqui te presentamos ventajas y desventajas de este tipo de estructura. Ventajas:")
                    texto_a_audio(datos['estructuras_de_datos']['pilas']['ventajas'])
                    texto_a_audio("Desventajas:")
                    texto_a_audio(datos['estructuras_de_datos']['pilas']['desventajas'])
                    
                elif respuesta == "colas":
                    image = Image.open("IMG/colas.png")
                    image = image.resize((790, 450))
                    photo = ImageTk.PhotoImage(image)
                    image_queue.put(photo)
                    send_text_to_ui("Colas:")
                    texto_a_audio(datos['estructuras_de_datos']['colas']['descripcion'])
                    texto_a_audio("aqui te presentamos ventajas y desventajas de este tipo de estructura. Ventajas:")
                    texto_a_audio(datos['estructuras_de_datos']['colas']['ventajas'])
                    texto_a_audio("Desventajas:")
                    texto_a_audio(datos['estructuras_de_datos']['colas']['desventajas'])

                elif respuesta == "hash":
                    image = Image.open("IMG/hash.png")
                    image = image.resize((790, 450))
                    photo = ImageTk.PhotoImage(image)
                    image_queue.put(photo)
                    send_text_to_ui("Hash:")
                    texto_a_audio(datos['estructuras_de_datos']['hash']['descripcion'])
                    texto_a_audio("aqui te presentamos ventajas y desventajas de este tipo de estructura. Ventajas:")
                    texto_a_audio(datos['estructuras_de_datos']['hash']['ventajas'])
                    texto_a_audio("Desventajas:")
                    texto_a_audio(datos['estructuras_de_datos']['hash']['desventajas'])

                send_text_to_ui("¿Deseas saber sobre otra estructura?\n1) Arreglos 2) Listas enlazadas 3) Pilas 4) Colas 5) Hash 6) No")
                texto_a_audio("¿Deseas saber sobre otra estructura?")

        elif respuesta == "programacion orientada a objetos":
            image = Image.open("IMG/poo.png")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            image_queue.put(photo)
            send_text_to_ui("Programacion Orientada a Objetos:")
            texto_a_audio(datos['POO']['definicion'])
            texto_a_audio("existen distintos conceptos importantes en Programacion Orientada a objetos, aqui te mostrare 5 de ellas.")
            send_text_to_ui("1) Clases 2) Objetos 3) Herencia 4) Polimorfismo 5) Encapsulamiento\n¿Por cual deseas empezar?")
            texto_a_audio("¿Por cual deseas empezar?")

            while True:

                respuesta = enviar_voz()

                if cond(respuesta) == True:
                    break

                if respuesta == "clases":
                    image = Image.open("IMG/clases.png")
                    image = image.resize((790, 450))
                    photo = ImageTk.PhotoImage(image)
                    image_queue.put(photo)
                    send_text_to_ui("Clases:")
                    texto_a_audio(datos['POO']['clases']['definicion'])
                    texto_a_audio("Observa el ejemplo")
                    texto_a_audio(datos['POO']['arrays']['ejemplo'])
                                    
                elif respuesta == "objetos":
                    image = Image.open("IMG/objetos.png")
                    image = image.resize((790, 450))
                    photo = ImageTk.PhotoImage(image)
                    image_queue.put(photo)
                    send_text_to_ui("Objetos:")
                    texto_a_audio(datos['POO']['objetos']['definicion'])
                    texto_a_audio("Observa el ejemplo")
                    texto_a_audio(datos['POO']['objetos']['ejemplo'])
                
                elif respuesta == "herencia":
                    image = Image.open("IMG/herencia.png")
                    image = image.resize((790, 450))
                    photo = ImageTk.PhotoImage(image)
                    image_queue.put(photo)
                    send_text_to_ui("Herencia:")
                    texto_a_audio(datos['POO']['herencia']['definicion'])
                    texto_a_audio("Observa el ejemplo")
                    texto_a_audio(datos['POO']['herencia']['ejemplo'])
                                        
                elif respuesta == "polimorfismo":
                    image = Image.open("IMG/polimorfismo.png")
                    image = image.resize((790, 450))
                    photo = ImageTk.PhotoImage(image)
                    image_queue.put(photo)
                    send_text_to_ui("Polimorfismo:")
                    texto_a_audio(datos['POO']['polimorfismo']['definicion'])
                    texto_a_audio("Observa el ejemplo")
                    texto_a_audio(datos['POO']['polimorfismo']['ejemplo'])
                
                elif respuesta == "encapsulamiento":
                    image = Image.open("IMG/encapsulamiento.png")
                    image = image.resize((790, 450))
                    photo = ImageTk.PhotoImage(image)
                    image_queue.put(photo)
                    send_text_to_ui("Encapsulamiento:")
                    texto_a_audio(datos['POO']['encapsulamiento']['definicion'])
                    texto_a_audio("Observa el ejemplo")
                    texto_a_audio(datos['POO']['encapsulamiento']['ejemplo'])

                send_text_to_ui("¿Deseas saber sobre otro concepto?\n1) Clases 2) Objetos 3) Herencia 4) Polimorfismo 5) Encapsulamiento 6) No")
                texto_a_audio("¿Deseas saber sobre otra estructura?")
        
        # btn_start = tk.Button(root, text="Volver a iniciar", command=start, 
        #               font=("Arial", 12, "bold"), 
        #               bg="#ffffff", fg="#555555", 
        #               borderwidth=0, 
        #               highlightthickness=0)

        # btn_start.grid(column=0, row=2, pady=10)    


    elif respuesta == "cuestionario":
        print ("Cuestionario")
        
        def comp(solucion, rpta):
            if rpta == solucion:
                tus_respuestas.append(1)
            else:
                tus_respuestas.append(0)

        image = Image.open("IMG/cuestionario.png")
        image = image.resize((790, 450))
        photo = ImageTk.PhotoImage(image)
        image_queue.put(photo)

        send_text_to_ui("Elegiste la opcion CUESTIONARIO.")
        texto_a_audio("Elegiste la opcion CUESTIONARIO.")
        texto_a_audio("Se te realizaran 10 preguntas y al final se te mostrara tu puntaje en conjunto de las justificaciones de las respuestas erroneas.")
        send_text_to_ui("¿Empezamos?\n1) Si 2) No")
        texto_a_audio("¿Estas listo?")

        respuesta = "si"

        if respuesta == "si":
            tus_respuestas = []
            image = Image.open("IMG/P1.jpg")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            image_queue.put(photo)
            send_text_to_ui("Pregunta 01\nElige sabiamente...")
            texto_a_audio(datos['PE_1'])

            respuesta = enviar_voz()

            comp(datos['P1_RESPUESTA'], respuesta)

            image = Image.open("IMG/P2.jpg")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            image_queue.put(photo)
            send_text_to_ui("Pregunta 02\nElige sabiamente...")
            texto_a_audio(datos['PE_2'])

            respuesta = enviar_voz()

            comp(datos['P2_RESPUESTA'], respuesta)

            image = Image.open("IMG/P3.jpg")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            image_queue.put(photo)
            send_text_to_ui("Pregunta 03\nElige sabiamente...")
            texto_a_audio(datos['PE_3'])

            respuesta = enviar_voz()

            comp(datos['P3_RESPUESTA'], respuesta)
            
            image = Image.open("IMG/P4.jpg")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            image_queue.put(photo)
            send_text_to_ui("Pregunta 04\nElige sabiamente...")
            texto_a_audio(datos['PE_4'], respuesta)

            respuesta = enviar_voz()

            comp(datos['P4_RESPUESTA'], respuesta)

            image = Image.open("IMG/P5.jpg")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            image_queue.put(photo)
            send_text_to_ui("Pregunta 05\nElige sabiamente...")
            texto_a_audio(datos['PE_5'])

            respuesta = enviar_voz()

            comp(datos['P5_RESPUESTA'], respuesta)

            image = Image.open("IMG/P6.jpg")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            image_queue.put(photo)
            send_text_to_ui("Pregunta 06\nElige sabiamente...")
            texto_a_audio(datos['PE_6'])

            respuesta = enviar_voz()

            comp(datos['P6_RESPUESTA'], respuesta)

            image = Image.open("IMG/P7.jpg")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            image_queue.put(photo)
            send_text_to_ui("Pregunta 07\nElige sabiamente...")
            texto_a_audio(datos['PE_7'])

            respuesta = enviar_voz()

            comp(datos['P7_RESPUESTA'], respuesta)

            image = Image.open("IMG/P8.jpg")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            image_queue.put(photo)
            send_text_to_ui("Pregunta 08\nElige sabiamente...")
            texto_a_audio(datos['PE_8'])

            respuesta = enviar_voz()

            comp(datos['P8_RESPUESTA'], respuesta)

            image = Image.open("IMG/P9.jpg")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            image_queue.put(photo)
            send_text_to_ui("Pregunta 09\nElige sabiamente...")
            texto_a_audio(datos['PE_9'])

            respuesta = enviar_voz()

            comp(datos['P9_RESPUESTA'], respuesta)

            image = Image.open("IMG/P10.jpg")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            image_queue.put(photo)
            send_text_to_ui("Pregunta 10\nElige sabiamente...")
            texto_a_audio(datos['PE_10'])

            respuesta = enviar_voz()

            comp(datos['P10_RESPUESTA'], respuesta)

            send_text_to_ui("Terminamos, veamos tus resultados...")
            texto_a_audio("Terminamos, veamos tus resultados...")

            t1 = "P"
            t2 = "_RESPUESTA"
            t3 = "_JUSTIFICACION"
            calificacion = 0
            
            for punto in tus_respuestas:
                if punto == 1:
                    calificacion + 1

            send_text_to_ui("Tu puntuacion ha sido de ", calificacion, " sobre 10.")
            texto_a_audio("Tu puntuacion ha sido de ", calificacion, " sobre 10.")

            for i, elemento in enumerate(tus_respuestas):
                if elemento == 1:
                    send_text_to_ui("Pregunta ", i+1, "\nRespuesta Correcta:", datos[t1+str(i+1)+t2])
                    texto_a_audio("Pregunta ", i+1, "\nRespuesta Correcta:", datos[t1+str(i+1)+t2])
                    texto_a_audio("debido a que", datos[t1+str(i+1)+t3])


    elif respuesta == "juegos":
        image = Image.open("IMG/perifericos.jpg")
        image = image.resize((790, 450))
        photo = ImageTk.PhotoImage(image)
        image_queue.put(photo)

        send_text_to_ui("Elegiste la opcion JUEGOS.")
        texto_a_audio("Elegiste la opcion JUEGOS.")
        send_text_to_ui("1) Laberinto de instrucciones 2) Ahorcados")
        texto_a_audio("Por el momento tenemos 2 juegos bastante divertidos, ¿cual te gustaria probar?")
        
        respuesta = "laberinto de instrucciones"

        if respuesta == "laberinto de instrucciones":

            image = Image.open("IMG/fondolaberinto.jpg")
            image = image.resize((790, 450))
            photo = ImageTk.PhotoImage(image)
            image_queue.put(photo)

            canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
            canvas.grid(column=0, row=0, pady=20)  # Posiciona el canvas en la columna 1

            grid = Grid(canvas, WIDTH, HEIGHT, CELL_SIZE)

            while True:
                send_text_to_ui("Escuchando tus indicaciones...")
                texto_a_audio("Escuchando tus indicaciones...")                
                respuesta = enviar_voz()
                if respuesta == "arriba":
                    grid.move_up(None)
                elif respuesta == "abajo":
                    grid.move_down(None)
                elif respuesta == "derecha":
                    grid.move_right(None)
                elif respuesta == "izquierda":
                    grid.move_left(None)
                else:
                    texto_a_audio("No es una dirección válida, dime una dirección válida.")

                if grid.user_cell == grid.goal_cell:
                    texto_a_audio("¡Felicidades, llegaste a tu destino!")
                    break
        
        elif respuesta == "ahorcados":

            image = Image.open("IMG/ahorcado1.jpg")
            image = image.resize((200, 300))
            photo = ImageTk.PhotoImage(image)
            image_queue.put(photo)

            send_text_to_ui("Empezamos con el juego")
            texto_a_audio("Empezamos con el juego")

            
            # 0 palabra, 1 cadena, 2 contador de errores
            palabra_elegida = datos['ahorcado'][random.randint(0, len(datos['ahorcado']) - 1)]
            ahorcado_info = [palabra_elegida, texto_ahorcado(palabra_elegida), 0]
            send_text_to_ui(ahorcado_info[1])

            while True:
                texto_a_audio("Elige una letra")
                mic_label.grid(column=0, row=2, pady=10)  
                letra = enviar_voz()            
                mic_label.grid_forget()
                

                print("se obtuvo la letra: " + letra[0])
                
                send_text_to_ui(ahorcado_info[1])
                yalas = set()

                yala = corroborar_letra(ahorcado_info, letra[0], yalas)
                if yala:
                    texto_a_audio("Ya elegiste esa palabra")
                else:
                    print("mi nueva cadena es")
                    print(ahorcado_info[1])
                    send_text_to_ui(ahorcado_info[1])

                    actualizaar_imagen_ahorcado(ahorcado_info[2])

                    if ahorcado_info[2] == 6:
                        texto_a_audio("perdiste")
                        break

    

def actualizaar_imagen_ahorcado(contador): 
    nombre = "IMG/ahorcado" + str(contador + 1) + ".jpg"
    image = Image.open(nombre)
    image = image.resize((200, 300))
    photo = ImageTk.PhotoImage(image)
    image_queue.put(photo)

def texto_ahorcado(palabra):
    cadena = ""

    for i in range(len(palabra) - 1):
        cadena += "_ "
    
    cadena += "_"

    return cadena

def corroborar_letra(info, letra, yalas):
    if letra in yalas:
        return True
    elif letra in info[0]:
        mensaje = "la letra:" + letra + " si se encuentra en la palabra"
        print(mensaje)
        yalas.add(letra)
        actualizar_cadena(info, letra)
    else:
        yalas.add(letra)
        info[2] = info[2] + 1

    return False

def actualizar_cadena(info, letra):
    for i in range(len(info[0])):
        if info[0][i] == letra:
            info[1] = info[1][:(2 * i)] + letra + info[1][(2 * i + 1):]

def cond(opcion):
                if opcion == "no":
                    return True
                else:
                    return False
                
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
        global photo
        photo = image_queue.get_nowait()     
        image_label.config(image = photo)
        print("de la ventana")
        print(root.winfo_reqwidth())
        print(photo.width())
        
        image_label.grid(column=0, row=0, pady=20, padx=((800 - photo.width())/ 2))



    except queue.Empty: 
        pass
        
    root.after(100, update_ui)

def start():
    queue_ui_to_main.put("start")

# Start the main thread
main_thread = threading.Thread(target=main_thread_logic)
main_thread.daemon = True
main_thread.start()

mic_image = ImageTk.PhotoImage(Image.open("IMG/mic_icon.png").resize((45, 45)))
mic_label = tk.Label(root, image=mic_image, bd=0, width=45, height=45)

btn_start = tk.Button(root, text="Iniciar", command=start, 
                      font=("Arial", 12, "bold"), 
                      bg="#ffffff", fg="#555555", 
                      borderwidth=0, 
                      highlightthickness=0)

btn_start.grid(column=0, row=2, pady=10)  

def on_enter(e):
    btn_start.config(font=("Arial", 14, "bold"))

def on_leave(e):
    btn_start.config(font=("Arial", 12, "bold"))

btn_start.bind("<Enter>", on_enter)
btn_start.bind("<Leave>", on_leave)

lbl_track=tk.Label(root, text=" ", font=("Arial", 13, "bold"))
lbl_text.config(bg="#262626",
                fg="#fefae4", # color mostaza
                font=("Oswald", 20, "bold")) 
lbl_text.grid(column=0, row=2)

# Run the main loop directly
root.mainloop()