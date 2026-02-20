import sys      # Importamos la libreria "sys" para poder leer los argumentos de la terminal
import socket   # Importamos "socket" para poder hacer conexiones de red
import os       # Importamos "os" para usar fork() y crear procesos hijos

# Paso 1
# Configuración del servidor
HOST = '127.0.0.1'

# Obtener puerto de línea de comandos o usar 8000 por defecto
if len(sys.argv) == 1:      # Si no escribimos argumentos ...
    PORT = 8000             # Usamos el puerto 8000 por defecto
    print(f"No se especificó puerto. Usando puerto por defecto: {PORT}")
else:                       # Si escribimos argumentos ...
    PORT = int(sys.argv[1]) # Cogemos el primer argumento como puerto

print(f"Servidor principal (PID: {os.getpid()}) iniciando...") # Mostramos el PID (identificador) de proceso principal

# Paso 2
# Crear el socket
s = socket.socket()
s.bind((HOST, PORT))    # Vinculamos el socket a la direccion y puerto elegido
s.listen(5)             # Escuchamos con cola de 5 clientes
print(f"Socket pasivo creado en {HOST}:{PORT}")

# Paso 3
# Definimos una función que se encarga de atender a un cliente
def dar_servicio(conn):
    """Atiende a un cliente: recibe datos y los envía de vuelta (eco)"""
    while True:
        data = conn.recv(1024)
        if not data:
            break
        conn.send(data)
    conn.close()

# Paso 4
# Creación de procesos hijos (pre-fork)
NUM_HIJOS = 3  # Vamos a crear 3 hijos

print(f"Creando {NUM_HIJOS} procesos hijos...")

for i in range(NUM_HIJOS):  # Bucle i =0,1,2
    pid = os.fork()         # Creamos un hijo
    
    if pid == 0:  # Este es el proceso HIJO
        break

# Paso 5
# Todos los procesos (padre y 3 hijos) llegan aquí
# Pero con diferentes valores de pid:
# - Hijos: pid = 0
# - Padre: pid > 0 (el PID del último hijo creado)

if pid == 0:
    # Esto lo ejecutan SOLO los HIJOS
    print(f"Hijo (PID: {os.getpid()}) listo para atender clientes")
else:
    # Esto lo ejecuta SOLO el PADRE
    print(f"Padre (PID: {os.getpid()}) listo para atender clientes")
    print(f"Total de procesos: {NUM_HIJOS + 1}")

# Paso 6
# Todos (padre e hijos) ejecutan este bucle
# Cada proceso es un servidor COMPLETO
while True:
    print(f"Proceso {os.getpid()} esperando cliente...")
    conn, addr = s.accept()  # Todos los procesos hacen accept()
    print(f"Proceso {os.getpid()} atiende a cliente {addr}")
    dar_servicio(conn)  # Atiende al cliente
    print(f"Proceso {os.getpid()} terminó de atender a {addr}")