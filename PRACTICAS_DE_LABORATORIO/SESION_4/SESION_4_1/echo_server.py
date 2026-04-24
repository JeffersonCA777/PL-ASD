import socket
import threading

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

def main():
    host = '0.0.0.0'
    port = 6000
    
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

if __name__ == '__main__':
    main()
