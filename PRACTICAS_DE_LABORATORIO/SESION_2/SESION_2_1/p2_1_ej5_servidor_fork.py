import sys      # Importamos la libreria "sys" para poder leer los argumentos de la terminal
import socket   # Importamos "socket" para poder hacer conexiones de red
import os       # Importamos "os" para usar fork() y crear procesos hijos
import signal   # Importamos "signal" para manejar señales SIGCHLD

# Paso 1
# Imprescindible: ignora señales de hijos muertos (evita zombies)
signal.signal(signal.SIGCHLD, signal.SIG_IGN)

# Paso 2
# Configuración del servidor
HOST = '127.0.0.1'  # Localhost

# Obtener puerto de línea de comandos o usar 8000 por defecto
if len(sys.argv) == 1:
    PORT = 8000
    print(f"Usando puerto por defecto: {PORT}")
else:
    PORT = int(sys.argv[1])

print(f"Servidor PADRE (PID: {os.getpid()}) iniciando...")

# Paso 3
# Crear el socket
s = socket.socket()
s.bind((HOST, PORT))
s.listen(5)
print(f"Socket pasivo creado en {HOST}:{PORT}")

# Función que atiende a un cliente 
def dar_servicio(conn):
    """Atiende a un cliente: recibe datos y los envía de vuelta"""
    while True:
        data = conn.recv(1024)
        if not data:  # Cliente cerró conexión
            break
        conn.send(data)  # ECO
    conn.close()  # Cerramos socket de datos

# Bucle principal del PADRE
while True:
    print(f"\n Padre esperando clientes...")
    conn, addr = s.accept()  # PADRE: acepta cliente
    print(f" Cliente conectado desde {addr}")
    
    # PADRE: crea un HIJO para atender a este cliente
    pid = os.fork()
    
    if pid == 0:  # Este es el HIJO
        # El HIJO cierra el socket pasivo (no lo necesita)
        s.close()
        print(f" Hijo (PID: {os.getpid()} atiende a {addr}")
        
        # HIJO: atiende al cliente
        dar_servicio(conn)
        
        # HIJO: termina su trabajo
        print(f" Hijo {os.getpid()} termina")
        sys.exit(0)  # El hijo MUERE aquí
    
    else:  # Este es el PADRE
        # El PADRE cierra el socket de datos (lo usará el hijo)
        conn.close()
        print(f" Padre vuelve a esperar...")