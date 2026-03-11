import socket # Para crear sockets 
import selectors # Para multiplexar sockets sin threads ni procesos
import random # Para generar números aleatorios para el juego

HOST = '0.0.0.0' # Escuchar en todas las interfaces
PORT = 8888 # Puerto donde el servidor escuchará conexiones

# Definimos las fases del juego como constantes
SALUDO = 1      # Esperando el nombre del jugador
JUGANDO = 2     # El jugador está adivinando el número
FIN = 3         # El jugador ha acertado y el juego ha terminado

class EstadoCliente: # Clase para guardar el estado de cada cliente conectado
    def __init__(self): # Inicializa el estado del cliente
        self.fase = SALUDO
        self.nombre = None
        self.numero = None
        self.intentos = 0
        self.buffer_salida = []  # Mensajes pendientes de enviar

def aceptar(sock, mask, selector): # Se llama cuando hay un cliente nuevo esperando conexión
    conn, addr = sock.accept()
    conn.setblocking(False)  # Importante: modo no bloqueante
    print(f"Jugador conectado: {addr}")
    
    estados[conn] = EstadoCliente() # Crear un nuevo estado para este cliente
    
    bienvenida = "Bienvenido/a al juego. ¿Cómo te llamas?\n"
    conn.send(bienvenida.encode("utf-8")) # Enviar mensaje de bienvenida al cliente

    selector.register(conn, selectors.EVENT_READ, atender_cliente) # Registrar el nuevo socket para leer datos del cliente

def atender_cliente(conn, mask, selector): # Se llama cuando un cliente conectado tiene datos para leer
    estado = estados.get(conn)
    if not estado:
        return
    
    try:
        data = conn.recv(1024) # Leer datos del cliente
        if not data:
            # Cliente desconectado
            raise ConnectionResetError
            
        linea = data.decode("utf-8").strip()

        if estado.fase == SALUDO: # Fase 1: Esperando el nombre del jugador
            estado.nombre = linea
            estado.numero = random.randint(1, 100)
            estado.intentos = 0
            estado.fase = JUGANDO
            respuesta = f"Hola {estado.nombre}, he pensado un numero entre 1 y 100.\n"
            conn.send(respuesta.encode("utf-8")) # Enviar mensaje de bienvenida y empezar el juego
            
        elif estado.fase == JUGANDO: # Fase 2: Adivinando números hasta acertar
            try:
                intento = int(linea)
                estado.intentos += 1
                
                if intento < estado.numero: # El número es mayor que el intento
                    respuesta = "Es mayor\n"
                elif intento > estado.numero: # El número es menor que el intento
                    respuesta = "Es menor\n"
                else:
                    respuesta = f"¡Acertaste, {estado.nombre}! ¡En {estado.intentos} intentos!\n"
                    estado.fase = FIN  # Pasa a fase final
                
                conn.send(respuesta.encode("utf-8"))
                
                if estado.fase == FIN: # Si ya acertó, cerramos la conexión después de enviar el mensaje final
                    selector.unregister(conn)
                    conn.close()
                    del estados[conn] # Limpiar el estado del cliente
                    
            except ValueError:
                conn.send("Por favor, introduce un numero\n".encode("utf-8"))
                
    except (ConnectionResetError, BrokenPipeError):
        print(f"Cliente {conn.getpeername()} desconectado") # Cliente se desconectó inesperadamente
        selector.unregister(conn) # Dejar de monitorear este socket
        conn.close() # Cerrar la conexión
        del estados[conn]

def main(): # Función principal para iniciar el servidor
    global estados
    estados = {}
    
    sel = selectors.DefaultSelector() # Crear selector
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Crear socket pasivo
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permitir reutilizar la dirección y el puerto
    sock.bind((HOST, PORT))
    sock.listen(5)
    sock.setblocking(False)  # No bloqueante para selectors
    
    print(f"Servidor SELECTORS escuchando en {HOST}:{PORT}")
    
    sel.register(sock, selectors.EVENT_READ, aceptar) # Registrar el socket pasivo en el selector
    
    # Bucle principal del selector
    while True:
        events = sel.select()  # Espera eventos
        for key, mask in events:
            # key.data es la función a llamar (aceptar o atender_cliente)
            callback = key.data
            callback(key.fileobj, mask, sel)

if __name__ == "__main__": # Ejecutar el servidor 
    main()