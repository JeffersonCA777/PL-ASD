import socket  # Importamos la librería que nos permite hacer conexiones de red

# Configuración del servidor
HOST = '127.0.0.1'  # Dirección IP  
PORT = 7000         # Puerto 

print('Inicializando socket...')  # Mensaje para saber que el programa empezó

# PASO 1: Crear el socket
s = socket.socket()  # Crea un socket TCP

# PASO 2: Asignar dirección y puerto al socket
s.bind((HOST, PORT))  # Conecta el socket con la dirección y puerto que definimos

# PASO 3: Poner el socket en modo escucha
s.listen(5) # Máximo 5 clientes pueden esperar en cola

# PASO 4: Bucle infinito para aceptar clientes
while True:
    # PASO 5: Esperar a que un cliente se conecte
    conn, addr = s.accept()
    
    # Mostramos quién se conectó
    print('Conectado con ->', addr)
    
    # PASO 6: Bucle para atender a ESTE cliente
    while True:
        # PASO 7: Recibir datos del cliente
        data = conn.recv(1024)
        
        # PASO 8: Mostrar cuántos bytes recibimos
        print(f'Recibidos {len(data)}')
        
        # PASO 9: Verificar si el cliente cerró la conexión
        if not data: 
            break  # Salimos del bucle interior (dejamos de atender a este cliente)
        
        # PASO 10: Enviar los mismos datos de vuelta (el "ECO")
        conn.send(data)
    
    # PASO 11: Cerrar la conexión con este cliente
    conn.close()

# PASO 12: Cerrar el socket principal
s.close()