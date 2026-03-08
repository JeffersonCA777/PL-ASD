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
        cliente, direccion = servidor.accept()
        print(f"Cliente conectado desde {direccion}")

        data = cliente.recv(1024).decode().strip()
        print(f"Recibido: {data}")

        partes = data.split()
        comando = partes[0] if partes else ""
        respuesta = ""

        if comando == "JOIN" and len(partes) == 4:
            _, nick, ip, puerto_str = partes
            try:
                puerto = int(puerto_str)
                if nick in registros:
                    respuesta = "ERROR\n"
                else:
                    registros[nick] = (ip, puerto)
                    respuesta = "OK\n"
            except ValueError:
                respuesta = "ERROR\n"

        elif comando == "LEAVE" and len(partes) == 2:
            _, nick = partes
            if nick in registros:
                del registros[nick]
                respuesta = "OK\n"
            else:
                respuesta = "ERROR\n"

        elif comando == "QUERY" and len(partes) == 2:
            _, nick = partes
            if nick in registros:
                ip, puerto = registros[nick]
                respuesta = f"OK {ip} {puerto}\n"  # Respuesta con formato: "OK IP PUERTO"
            else:
                respuesta = "ERROR\n"

        else:
            respuesta = "ERROR\n"
            print(f"Comando inválido: {data}")

        cliente.send(respuesta.encode())
        cliente.close()

except KeyboardInterrupt:
    print("\nBroker detenido por el usuario")
finally:
    servidor.close()