import socket # Para crear conexiones de red (TCP/UDP)

HOST = '0.0.0.0'  # Escuchar en todas las interfaces de red
PUERTO = 11111   # Puerto donde el broker escuchará
registros = {}  # Diccionario para almacenar los clientes registrados (IP, puerto)

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crear socket TCP
servidor.bind((HOST, PUERTO))  # Asociar el socket a la dirección y puerto
servidor.listen(5)  # El socket espera conexiones entrantes (máximo 5 en cola)
print(f"Broker escuchando en {HOST}:{PUERTO}...")

try: # El bloque principal del servidor, que se ejecuta indefinidamente hasta que se interrumpe
    while True: # El servidor escucha para siempre
        cliente, direccion = servidor.accept()  # Aceptar una conexión entrante
        print(f"Cliente conectado desde {direccion}")

        data = cliente.recv(1024).decode().strip()  # Recibir datos del cliente
        print(f"Recibido: {data}")

        partes = data.split() # Dividir el mensaje en partes para procesar comandos
        comando = partes[0] if partes else ""  # El primer elemento es el comando
        respuesta = ""  # Variable para almacenar la respuesta que se enviará al cliente

        if comando == "JOIN" and len(partes) == 4: # Comando para unirse al broker debe tener 4 partes: JOIN <nick> <ip> <puerto>
            _, nick, ip, puerto_str = partes # Extraer el nick, IP y puerto del mensaje
            try:
                puerto = int(puerto_str) # Convertir el puerto a entero
                if nick in registros: # Verificar si el nick ya está registrado
                    respuesta = "ERROR\n" # Si el nick ya existe, enviar un error
                else:
                    registros[nick] = (ip, puerto) # Registrar el nuevo cliente en el diccionario
                    respuesta = "OK\n" # Enviar confirmación de registro exitoso
            except ValueError:
                respuesta = "ERROR\n" # Si el puerto no es un número válido, enviar un error

        elif comando == "LEAVE" and len(partes) == 2: # Comando para salir del broker debe tener 2 partes: LEAVE <nick>
            _, nick = partes # Extraer el nick del mensaje
            if nick in registros: # Verificar si el nick está registrado
                del registros[nick] # Eliminar el cliente del diccionario de registros
                respuesta = "OK\n" # Enviar confirmación de salida exitosa
            else:
                respuesta = "ERROR\n" # Si el nick no existe, enviar un error

        elif comando == "QUERY" and len(partes) == 2: # Comando para consultar la lista de clientes registrados debe tener 2 partes: QUERY <nick>
            _, nick = partes # Extraer el nick del mensaje
            if nick in registros: # Verificar si el nick está registrado
                ip, puerto = registros[nick] # Obtener la IP y puerto del cliente registrado
                respuesta = f"{ip} {puerto}\n" # Enviar la información del cliente
            else:
                respuesta = "ERROR\n" # Si el nick no existe, enviar un error

        else:
            respuesta = "ERROR\n" # Si el comando no es reconocido o tiene formato incorrecto, enviar un error
            print(f"Comando inválido: {data}") # Imprimir un mensaje de error para comandos no válidos

        cliente.send(respuesta.encode()) # Enviar la respuesta al cliente
        cliente.close() # Cerrar la conexión con el cliente

except KeyboardInterrupt: # Permitir cerrar el servidor con Ctrl+C
    print("\nBroker detenido por el usuario") # Imprimir un mensaje al detener el servidor
finally: # Asegurar que el socket se cierre al finalizar
    servidor.close() # Cerrar el socket del servidor

