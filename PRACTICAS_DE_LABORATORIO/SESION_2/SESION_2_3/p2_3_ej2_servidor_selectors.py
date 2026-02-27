import socket # Importamos para crear y manejar sockets que nos permite hacer conexiones de red
import selectors # Importamos para crear la multiplexación moderna 

# CONFIGURACIÓN
HOST = '' # Escuchar en todas las direcciones
PORT = 7000 # Puerto donde se escuchará

# PASO 1: Crear el selector (el organizador)
selector = selectors.DefaultSelector() # Elige el mejor metodo segun el sistema operativo

# PASO 2: Función para aceptar nuevos clientes
def aceptar_cliente(sock, mask):    # sock-socket que tiene actividad, mask-indicar si lectura/escritura
    cliente, direccion = sock.accept()
    cliente.setblocking(False)
    # Registrar al nuevo cliente con su función de atención
    selector.register(cliente, selectors.EVENT_READ, atender_cliente)
    print(f"Cliente conectado desde {direccion}")

# PASO 3: Función para atender clientes existentes
def atender_cliente(sock, mask):
    datos = sock.recv(1024)
    if datos:
        sock.send(datos)
        print(f"Eco: {datos.decode().strip()}")
    else:
        print("Cliente desconectado")
        selector.unregister(sock)  # Quitar del selector
        sock.close()

# PASO 4: Crear el socket del servidor
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((HOST, PORT))
servidor.listen(5)
servidor.setblocking(False)

# PASO 5: Registrar el socket del servidor en el selector
selector.register(servidor, selectors.EVENT_READ, aceptar_cliente)
print(f"Servidor escuchando en puerto {PORT}")

# PASO 6: Bucle principal (el reactor)
while True:
    eventos = selector.select()  # Esperar eventos
    for key, mask in eventos:
        # key.data contiene la función que registramos
        callback = key.data
        # Llamar a la función correspondiente
        callback(key.fileobj, mask)