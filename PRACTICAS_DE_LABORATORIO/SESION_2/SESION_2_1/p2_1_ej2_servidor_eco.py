import sys      # Importamos la libreria "sys" para poder leer los argumentos de la terminal
import socket   # Importamos "socket" para poder hacer conexiones de red

# Paso 1
# Configuración del servidor
HOST = '127.0.0.1'                    # Localhost
PORT = int(sys.argv[1])               # El puerto lo cogemos desde la terminal

print(f'Inicializando socket en el puerto {PORT}...') # Mostramos el puerto eligido

# Paso 2
# Crear el socket
s = socket.socket()
s.bind((HOST, PORT)) # Vinculamos el socket a la direccion y puerto elegido
s.listen(5) # El socket escucha un máximo de 5 clientes en cola

print(f'Servidor escuchando en {HOST}:{PORT}')

#Paso 3
# Bucle principal para aceptar clientes
while True:
    conn, addr = s.accept()
    print(f'Conectado con -> {addr}')

   # Bucle para atender a este cliente 
    while True:
        data = conn.recv(1024) # Recibimos los datos (máximo de 1024 bytes)
        print(f'Recibidos {len(data)} bytes')

        # Si no hay datos, el cliente se desconectó
        if not data: 
            print(f'Cliente {addr} desconectado')
            break
        conn.send(data) # Enviamos los datos de vuelta (Eco)
        print(f'Enviados {len(data)} bytes')
    
    conn.close() # Cerramos la conexión con este cliente

s.close() 