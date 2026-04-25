"""
Servidor echo multi-hilo para el de despliegue de servicios en contenedores.
Este servidor escucha en el puerto 6000 y devuelve (hace echo) de todos los datos
que recibe de los clientes conectados. 
"""

# 1. Librerias
import socket
import threading

# 2. Funcion para manejar cada cliente
def handle_client(conn, addr):
    print(f"[+] Conexión desde {addr}")
    while True:
        data = conn.recv(1024)
        if not data:
            break
        print(f"[{addr}] Recibido: {data.decode().strip()}")
        conn.sendall(data)  # Echo: devuelve lo mismo
    print(f"[-] Conexión cerrada: {addr}")
    conn.close()

# 3. Funcion principal
def main():
    host = '0.0.0.0'
    port = 6000 # Incia el puerto 6000 para el servidor echo
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"[*] Servidor echo escuchando en {host}:{port}")
    
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.daemon = True
        thread.start()

# 4. Punto de entrada del programa
if __name__ == '__main__':
    main()