import socket # Para crear el socket del servidor
import random # Para generar el número aleatorio que el cliente debe adivinar

HOST = '0.0.0.0' # Escuchar en todas las interfaces de red disponibles
PORT = 8888 # Puerto en el que el servidor escuchará las conexiones entrantes

def jugar(conn): # Función que maneja la lógica del juego con un cliente conectado
    conn.sendall("Bienvenido/a al juego. ¿Cómo te llamas?\n".encode("utf-8")) # Pedimos el nombre del jugador
    
    nombre = conn.recv(1024).decode("utf-8").strip() # # Leemos el nombre del jugador desde el socket y lo decodificamos
    
    numero = random.randint(1, 100) # # Pensamos el número aleatorio entre 1 y 100 que el jugador debe adivinar
    intentos = 0 # Contador de intentos del jugador
    
    conn.sendall(f"Hola {nombre}, he pensado un numero entre 1 y 100.\n".encode("utf-8")) # # Mensaje de inicio del juego para el jugador
    
    while True: # # Bucle principal del juego
        conn.sendall(b"Adivina: ") # Pedimos al jugador que adivine el número
        linea = conn.recv(1024).decode("utf-8").strip() # Leemos la respuesta del jugador desde el socket y la decodificamos
        
        if not linea: # Si el cliente se desconecta, terminamos el juego
            break

        try: # Intentamos convertir a número el intento del jugador
            intento = int(linea)
            intentos += 1 # Incrementamos el contador de intentos
            
            # Comprobamos el intento
            if intento < numero:
                conn.sendall("Es mayor\n".encode("utf-8"))
            elif intento > numero:
                conn.sendall("Es menor\n".encode("utf-8"))
            else:
                conn.sendall(f"¡Acertaste, {nombre}! ¡En {intentos} intentos!\n".encode("utf-8"))
                break
                
        except ValueError: # Si el jugador no introduce un número válido, le pedimos que lo intente de nuevo
            conn.sendall("Por favor, introduce un numero\n".encode("utf-8"))

def main():
    
    sp = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Crear socket TCP (AF_INET para IPv4, SOCK_STREAM para TCP)
    
    sp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permitir reusar la dirección (útil para reinicios rápidos)
    
    sp.bind((HOST, PORT)) # Asociar socket a dirección y puerto 
    
    sp.listen(5) # Poner el socket en modo escucha
    print(f"Servidor Iterativo escuchando en {HOST}:{PORT}")
    
    # Bucle principal del servidor
    while True:
        
        sd, addr = sp.accept() # Aceptar una conexión entrante 
        print(f"Jugador conectado: {addr}")
        
        jugar(sd) # Jugar con el cliente (aquí se bloquea hasta que termine)
        
        sd.close() # Cerrar la conexión con el cliente después de que termine el juego

if __name__ == "__main__": # Punto de entrada del programa
    main()