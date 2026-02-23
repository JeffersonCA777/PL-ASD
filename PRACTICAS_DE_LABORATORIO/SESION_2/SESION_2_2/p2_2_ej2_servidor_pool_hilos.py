import sys          # Importamos la libreria "sys" para poder leer los argumentos de la terminal
import socket       # Importamos "socket" para poder hacer conexiones de red
import threading    # Importamos la libreria "threading" para poder crear hilos
import queue        # Importamos la libreria "queue" para crear colas

# FUNCIÓN DEL HILO JEFE: acepta clientes y los pone en cola
def servidor_jefe(cola, puerto):
    HOST = "127.0.0.1"
    
    # Crear socket del servidor
    servidor = socket.socket()
    servidor.bind((HOST, puerto))
    servidor.listen(5)
    print(f"[JEFE] Servidor escuchando en {HOST}:{puerto}")
    
    while True:
        print("[JEFE] Esperando clientes...")
        conn, addr = servidor.accept()      # Esperar cliente
        print(f"[JEFE] Cliente {addr} conectado. Metiendo en cola...")
        cola.put(conn)  # Pone el socket en la cola (si está llena, espera)

# FUNCIÓN DEL HILO TRABAJADOR: atiende clientes de la cola
def servidor_trabajador(cola, num):
    while True:
        print(f"[TRABAJADOR {num}] Esperando trabajo...")
        conn = cola.get()  # Saca un socket de la cola (si está vacía, espera)
        addr = conn.getpeername()
        print(f"[TRABAJADOR {num}] Atendiendo a {addr}")
        
        while True:
            datos = conn.recv(1024)
            if not datos:
                break
            print(f"[TRABAJADOR {num}] Recibido: {datos.decode()}")
            conn.send(datos)
        
        conn.close()
        print(f"[TRABAJADOR {num}] Cliente {addr} desconectado")

# PROGRAMA PRINCIPAL
if __name__ == "__main__":
    # Leer argumentos: N y PUERTO
    if len(sys.argv) != 3:
        print("Uso: python3 p2_2_ej2_servidor_pool_hilos.py <N> <PUERTO>")
        print("Ejemplo: python3 p2_2_ej2_servidor_pool_hilos.py 3 8888")
        sys.exit(1)
    
    N = int(sys.argv[1])      # Número de trabajadores
    PORT = int(sys.argv[2])   # Puerto
    
    print(f"=== SERVIDOR CON POOL DE {N} HILOS ===")
    
    cola = queue.Queue(N)   # Crear cola de tamaño N
    
    # Crear y lanzar el hilo JEFE
    jefe = threading.Thread(target=servidor_jefe, args=(cola, PORT))
    jefe.daemon = True
    jefe.start()
    
    # Crear y lanzar los N hilos TRABAJADORES
    for i in range(N):
        trabajador = threading.Thread(target=servidor_trabajador, args=(cola, i+1))
        trabajador.daemon = True
        trabajador.start()
    
    # Mantener el programa principal vivo
    try:
        while True:
            # Mostrar estado cada 5 segundos
            threading.Event().wait(5)
            print(f"\n[ESTADO] Hilos activos: {threading.active_count()} (1 jefe + {N} trabajadores)")
            print(f"[ESTADO] Tamaño cola: {cola.qsize()}/{N}\n")
    except KeyboardInterrupt:
        print("\n Servidor detenido por el usuario")