import socket # Para crear el socket del servidor
import random # Para generar el número aleatorio que el cliente debe adivinar
import threading  # Para manejar cada cliente en un hilo separado

HOST = '0.0.0.0' # Escuchar en todas las interfaces de red disponibles
PORT = 8888 # Puerto en el que el servidor escuchará las conexiones entrantes

def jugar(conn): # Esta función es IGUAL que en el ej0, pero ahora cada cliente se ejecuta en un hilo diferente
    
    conn.sendall("Bienvenido/a al juego. ¿Cómo te llamas?\n".encode("utf-8"))
    
    nombre = conn.recv(1024).decode("utf-8").strip() # Leemos el nombre del jugador desde el socket y lo decodificamos
    numero = random.randint(1, 100) # Pensamos el número aleatorio entre 1 y 100 que el jugador debe adivinar
    intentos = 0
    
    conn.sendall(f"Hola {nombre}, he pensado un numero entre 1 y 100.\n".encode("utf-8")) # Mensaje de inicio del juego para el jugador
    
    while True:
        conn.sendall(b"Adivina: ") # Pedimos al jugador que adivine el número
        linea = conn.recv(1024).decode("utf-8").strip() # Leemos la respuesta del jugador desde el socket y la decodificamos
        
        if not linea:
            break
        
        try:
            intento = int(linea) # Intentamos convertir a número el intento del jugador
            intentos += 1 # Incrementamos el contador de intentos
            
            if intento < numero: # Comprobamos el intento
                conn.sendall("Es mayor\n".encode("utf-8"))
            elif intento > numero: # Comprobamos el intento
                conn.sendall("Es menor\n".encode("utf-8"))
            else:
                conn.sendall(f"¡Acertaste, {nombre}! ¡En {intentos} intentos!\n".encode("utf-8"))
                break
                
        except ValueError: # Si el jugador no introduce un número válido, le pedimos que lo intente de nuevo
            conn.sendall("Por favor, introduce un numero\n".encode("utf-8"))
    
    conn.close() # Cuando el jugador termina, cerramos la conexión

def main(): # Función principal del servidor
    sp = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Crear socket TCP (AF_INET para IPv4, SOCK_STREAM para TCP)
    sp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permitir reusar la dirección 
    sp.bind((HOST, PORT))
    sp.listen(5)
    print(f"Servidor CON HILOS escuchando en {HOST}:{PORT}")
    
    while True:
        
        sd, addr = sp.accept() # Aceptamos un nuevo cliente y obtenemos su socket y dirección
        print(f"Jugador conectado: {addr}")
        
        hilo = threading.Thread(target=jugar, args=(sd,)) # Creamos un nuevo hilo que ejecutará la función jugar con el socket del cliente como argumento
        hilo.start() # Iniciamos el hilo, que comenzará a ejecutar la función jugar para ese cliente

if __name__ == "__main__": # Punto de entrada del programa
    main()