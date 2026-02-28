import socket   # Importamos para crear y manejar sockets que nos permitirá conexiones de red
import selectors    # Importamos para crear la multiplexación moderna

# CONFIGURACIÓN
HOST = ''   # Escuchar en todas las direcciones
PUERTO_ECO = 7777   # Puerto para servicio eco
PUERTO_MAYUS = 7778 # Puerto para servicio eco en mayusculas

# 1. CREAR SELECTOR
selector = selectors.DefaultSelector()  # Elige el mejor metodo segun el sistema operativo

# 2. FUNCIONES PARA SERVICIO ECO
def atender_eco(sock, mask):    # sock-socket que tiene actividad, mask-indicar si lectura/escritura
    datos = sock.recv(1024)
    if datos:
        sock.send(datos)  # Eco: devuelve lo mismo
        print(f"[ECO] {datos.decode().strip()}")
    else:
        print("[ECO] Cliente desconectado")
        selector.unregister(sock)
        sock.close()

def aceptar_eco(sock, mask):
    cliente, direccion = sock.accept()
    cliente.setblocking(False)
    selector.register(cliente, selectors.EVENT_READ, atender_eco)
    print(f"[ECO] Cliente conectado desde {direccion}")

# 3. FUNCIONES PARA SERVICIO MAYÚSCULAS
def atender_mayus(sock, mask):
    datos = sock.recv(1024)
    if datos:
        mensaje = datos.decode().strip().upper()  # Convertir a mayúsculas
        sock.send(mensaje.encode())
        print(f"[MAYÚS] {mensaje}")
    else:
        print("[MAYÚS] Cliente desconectado")
        selector.unregister(sock)
        sock.close()

def aceptar_mayus(sock, mask):
    cliente, direccion = sock.accept()
    cliente.setblocking(False)
    selector.register(cliente, selectors.EVENT_READ, atender_mayus)
    print(f"[MAYÚS] Cliente conectado desde {direccion}")

# 4. CREAR SOCKET PARA SERVICIO ECO
sock_eco = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_eco.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock_eco.bind((HOST, PUERTO_ECO))
sock_eco.listen(5)
sock_eco.setblocking(False)
selector.register(sock_eco, selectors.EVENT_READ, aceptar_eco)
print(f"Servidor ECO escuchando en puerto {PUERTO_ECO}")

# 5. CREAR SOCKET PARA SERVICIO MAYÚSCULAS
sock_mayus = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_mayus.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock_mayus.bind((HOST, PUERTO_MAYUS))
sock_mayus.listen(5)
sock_mayus.setblocking(False)
selector.register(sock_mayus, selectors.EVENT_READ, aceptar_mayus)
print(f"Servidor MAYÚSCULAS escuchando en puerto {PUERTO_MAYUS}")

# 6. BUCLE PRINCIPAL (REACTOR)
print("Servidor listo. Esperando conexiones...")
while True:
    eventos = selector.select()
    for key, mask in eventos:
        callback = key.data
        callback(key.fileobj, mask)