import socket   # Importamos para crear y manejar los sockets
import select   # Importamos para crear la multilplexación 

# CONFIGURACIÓN
HOST = ''  # Escuchar en todas las direcciones
PORT = 7000  # Puerto donde escuchará

# PASO 1: Crear el socket pasivo
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # Crear el socket pasivo (servidor)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((HOST, PORT)) # Asignarle al socket dirección y puerto
servidor.listen(5)
servidor.setblocking(False)  # Modo no bloqueante
print(f"Servidor escuchando en puerto {PORT}")

# PASO 2: Lista de sockets a vigilar (solo lectura)
sockets_vigilados = [servidor]

# PASO 3: Bucle principal del servidor
while True:
    # Preguntamos al vigilante: ¿qué sockets tienen datos?
    listos_lectura, _, _ = select.select(sockets_vigilados, [], [])
    
    for socket_activo in listos_lectura:    # Revisamos cada socket que tiene datos
        # CASO 1: Es un cliente nuevo (socket pasivo)
        if socket_activo is servidor:
            cliente, direccion = servidor.accept()
            cliente.setblocking(False)
            sockets_vigilados.append(cliente)
            print(f"Cliente conectado desde {direccion}")
        
        # CASO 2: Es un cliente existente
        else:
            datos = socket_activo.recv(1024)
            if datos:
                # Devolvemos el eco
                socket_activo.send(datos)
                print(f"Eco: {datos.decode().strip()}")
            else:
                # Cliente desconectó
                print("Cliente desconectado")
                socket_activo.close()
                sockets_vigilados.remove(socket_activo)