import socket   # Importamos para crear y manejar sockets que nos permite hacer conexiones de red
import selectors    # Importamos para crear la multiplexación moderna

# CONFIGURACIÓN
HOST = ''   # Escuchar en todas las direcciones
PORT = 7000 # Puerto donde se escuchará

# 1. CREAR SELECTOR
selector = selectors.DefaultSelector() # Elige el mejor método según el sistema operativo

# 2. FUNCIÓN PARA ENVIAR MENSAJE A TODOS
def enviar_a_todos(mensaje, socket_remitente=None): # Es una función que recibe lo que queremos enviar y el socket que envió el mensaje
    """Envía un mensaje a todos los clientes excepto al remitente (opcional)"""
    for key in selector.get_map().values(): # Obtiene todos los sockets registrados
        if key.data is manejar_cliente:  # Solo a clientes, no al servidor
            if key.fileobj != socket_remitente:  # Opcional: no enviar al que envió
                try:
                    key.fileobj.send(mensaje)
                except:
                    pass    # Si hay error, ignoramos (el cliente se desconectó)

# 3. FUNCIÓN PARA MANEJAR CLIENTES
def manejar_cliente(sock, mask):
    datos = sock.recv(1024)
    if datos:
        print(f"Recibido: {datos.decode().strip()}")
        # Enviar a TODOS los clientes
        enviar_a_todos(datos, sock)
    else:
        print("Cliente desconectado")
        selector.unregister(sock)
        sock.close()

# 4. FUNCIÓN PARA ACEPTAR NUEVOS CLIENTES
def aceptar_cliente(sock, mask):
    cliente, direccion = sock.accept()
    cliente.setblocking(False)
    selector.register(cliente, selectors.EVENT_READ, manejar_cliente)
    print(f"Cliente conectado desde {direccion}")

# 5. CREAR SOCKET DEL SERVIDOR
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((HOST, PORT))
servidor.listen(5)
servidor.setblocking(False)

# 6. REGISTRAR SERVIDOR
selector.register(servidor, selectors.EVENT_READ, aceptar_cliente)
print(f"Servidor CHAT MULTIPLE escuchando en puerto {PORT}")

# 7. BUCLE PRINCIPAL
while True:
    eventos = selector.select()
    for key, mask in eventos:
        callback = key.data
        callback(key.fileobj, mask)