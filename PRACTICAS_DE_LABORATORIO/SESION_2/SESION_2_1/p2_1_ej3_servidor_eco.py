import sys      # Importamos la libreria "sys" para poder leer los argumentos de la terminal
import socket   # Importamos "socket" para poder hacer conexiones de red

# Paso 1
# Configuración del servidor
HOST = '127.0.0.1'
PORT = int(sys.argv[1]) # El puerto lo cogemos desde la terminal

print(f'Inicializando socket en el puerto {PORT}...')

# Paso 2
# Crear el socket
s = socket.socket() # Vinculamos el socket a la direccion y puerto elegido
s.bind((HOST, PORT))
s.listen(5)

print(f'Servidor escuchando en {HOST}:{PORT}')

# Paso 3
# Definimos una función que se encarga de atender a un cliente
def dar_servicio(conn):
    """Atiende a un cliente: recibe datos y los envía de vuelta (eco)"""
    while True:
        data = conn.recv(1024)
        print(f'📥 Recibidos {len(data)} bytes')
        if not data:
            print(f'Cliente desconectado')
            break
        conn.send(data)
        print(f'Enviados {len(data)} bytes')
    conn.close()

# Paso 4
# Bucle principal del servidor
while True:
    conn, addr = s.accept()
    print(f'Conectado con -> {addr}')
    
    # Llamamos a la función para atender a este cliente
    dar_servicio(conn)

# Nunca se ejecuta
s.close()