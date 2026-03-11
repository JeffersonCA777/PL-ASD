import socket  # Para crear conexiones de red (TCP/UDP)

HOST = '0.0.0.0'  # Escuchar en todas las interfaces de red
PUERTO = 11111   # Puerto donde el broker escuchará
registros = {}  # Diccionario para almacenar los clientes registrados (IP, puerto)

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crear socket TCP
servidor.bind((HOST, PUERTO))  # Asociar el socket a la dirección y puerto
servidor.listen(5)  # El socket espera conexiones entrantes (máximo 5 en cola)
print(f"Broker escuchando en {HOST}:{PUERTO}...")

try:
    while True:
        cliente, direccion = servidor.accept() # Esperar a que un cliente se conecte
        print(f"Cliente conectado desde {direccion}")

        data = cliente.recv(1024).decode().strip() # Recibir datos del cliente y decodificar a string
        print(f"Recibido: {data}")

        partes = data.split() # Dividir el comando en partes
        comando = partes[0] if partes else ""
        respuesta = ""

        if comando == "JOIN" and len(partes) == 4: # Comando JOIN con formato: "JOIN NICK IP PUERTO"
            _, nick, ip, puerto_str = partes # Extraer los componentes del comando
            try:
                puerto = int(puerto_str) # Convertir el puerto a entero
                if nick in registros: # Verificar si el nick ya está registrado
                    respuesta = "ERROR\n"
                else:
                    registros[nick] = (ip, puerto) # Registrar el cliente con su IP y puerto
                    respuesta = "OK\n"
            except ValueError: # Manejar el caso donde el puerto no es un número válido
                respuesta = "ERROR\n"

        elif comando == "LEAVE" and len(partes) == 2: # Comando LEAVE con formato: "LEAVE NICK"
            _, nick = partes
            if nick in registros: # Verificar si el nick está registrado para eliminarlo
                del registros[nick]
                respuesta = "OK\n"
            else:
                respuesta = "ERROR\n"

        elif comando == "QUERY" and len(partes) == 2: # Comando QUERY con formato: "QUERY NICK"
            _, nick = partes
            if nick in registros: # Verificar si el nick está registrado para obtener su IP y puerto
                ip, puerto = registros[nick]
                respuesta = f"OK {ip} {puerto}\n"  # Respuesta con formato: "OK IP PUERTO"
            else:
                respuesta = "ERROR\n"

        else:
            respuesta = "ERROR\n"
            print(f"Comando inválido: {data}")

        cliente.send(respuesta.encode()) # Enviar la respuesta al cliente codificada a bytes
        cliente.close() # Cerrar la conexión con el cliente después de procesar su solicitud

except KeyboardInterrupt: # Permitir detener el broker con Ctrl+C
    print("\nBroker detenido por el usuario")
finally:
    servidor.close() # Cerrar el socket del servidor al finalizar