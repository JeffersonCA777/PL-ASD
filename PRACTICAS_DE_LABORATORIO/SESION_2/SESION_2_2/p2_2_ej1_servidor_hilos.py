import sys
import socket
import threading # Importamos la libreria "threading" para poder crear hilos

# Función que ejecuta cada hilo para atender a UN cliente
def atender_cliente(conn):
    while True:
        datos = conn.recv(1024) # Esperar mensaje del cliente
        if not datos:
            break
        conn.send(datos)        # Enviar eco
    conn.close()                # Cerrar conexión

# Configurar puerto
if len(sys.argv) == 1:      # Si ejecutas sin argumentos
    PORT = 8000             # Usa puerto 8000 por defecto
else:
    PORT = int(sys.argv[1]) # Si ejecutas con argumento, usa ese puerto

HOST = "127.0.0.1"

# Crear socket del servidor
print("Arrancando servidor...")
s = socket.socket()
s.bind((HOST, PORT))
s.listen(5)
print(f"Servidor escuchando en {HOST}:{PORT}")

# Bucle principal: esperar clientes y crear hilos
while True:
    print("Esperando clientes... (Ctrl+C para salir)")
    conn, addr = s.accept() # Esperar al cliente 
    print(f"Cliente conectado desde {addr}")
    
    hilo = threading.Thread(target=atender_cliente, args=(conn,))   # Crear el hilo. A tiende al cliente
    hilo.daemon = True  # Hilo temporal
    hilo.start()        # Empieza el hilo a trabajar u operar
    print(f"Hilos activos: {threading.active_count()}")