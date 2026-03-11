import asyncio # Para programación asíncrona
import sys # Para acceder a argumentos de línea de comandos
from redis.asyncio import Redis  # Redis asíncrono para Python 

class ChatProtocol(asyncio.DatagramProtocol): # Protocolo para manejar mensajes UDP
    def datagram_received(self, data, addr): # Cuando llega un mensaje, lo decodificamos y lo mostramos
        mensaje = data.decode()
        print(f"\n{mensaje}")
        print("> ", end="", flush=True)

async def get_my_ip(): # Función para obtener la IP local 
    reader, writer = await asyncio.open_connection("8.8.8.8", 53)
    ip_local = writer.get_extra_info('sockname')[0] # Obtenemos la IP local desde el socket
    writer.close()
    return ip_local

async def shell_interactiva(transport, nick, redis_client): # Función para manejar la shell interactiva del chat
    reader = asyncio.StreamReader() # Creamos un StreamReader para leer la entrada del usuario de forma asíncrona
    protocol = asyncio.StreamReaderProtocol(reader) # Asociamos el StreamReader a un protocolo para poder usarlo con asyncio
    loop = asyncio.get_running_loop() # Obtenemos el loop de eventos actual
    await loop.connect_read_pipe(lambda: protocol, sys.stdin) # Conectamos el StreamReader a la entrada

    destino = None  # Ip y puerto del destinatario

    while True:
        print("> ", end="", flush=True)
        linea_bytes = await reader.readline() # Leemos una línea de la entrada del usuario (en bytes)
        if not linea_bytes:
            break

        linea = linea_bytes.decode().strip() # Decodificamos la línea a string y eliminamos espacios en blanco

        if not linea:
            continue

        if linea.startswith("/QUIT"): # QUIT: Salir del chat
            await redis_client.hdel("chat:usuarios", nick) # Dar de baja en Redis
            print("¡Saliendo...!")
            break

        elif linea.startswith("/CONNECT"): # CONNECT: Establecer destino para enviar mensajes
            partes = linea.split()
            if len(partes) == 2: # El usuario debe escribir: /CONNECT <nick>
                nick_buscar = partes[1]

                valor = await redis_client.hget("chat:usuarios", nick_buscar) # Consultamos en Redis 

                if valor:
                    ip, puerto_str = valor.split(':') # El valor es "IP:puerto", lo separamos
                    destino = (ip, int(puerto_str))
                    print(f"Conectado a {nick_buscar} en {ip}:{puerto_str}")
                else:
                    print(f"Error: Usuario '{nick_buscar}' no encontrado")
            else:
                print("Uso: /CONNECT <nick>")

        else:
            if destino is None: # Si no se ha establecido un destino, no podemos enviar mensajes
                print("Error: No has establecido un destino. Usa /CONNECT <nick>")
            else:
                mensaje = f"{nick}> {linea}"
                transport.sendto(mensaje.encode(), destino) # Enviamos el mensaje al destino establecido

async def main(): # Función principal del programa
    if len(sys.argv) != 2:  # ¡Solo necesita el nick!
        print("Uso: python3 p2_5_ej5opc_chat_redis.py <nick>")
        print("(Redis debe estar corriendo en localhost:6379)")
        return

    nick = sys.argv[1] # El nick del usuario, que se usará para registrarse en Redis y mostrar en los mensajes

    # 1. Conectar a Redis
    try:
        redis_client = Redis( # Conexión asíncrona a Redis
            host='localhost',
            port=6379,
            decode_responses=True  # Decodificar respuestas como strings en lugar de bytes
        )
        await redis_client.ping() # Verificar que la conexión a Redis funciona
        print("Conectado a Redis")
    except Exception as e: # Si hay un error al conectar a Redis, lo mostramos y damos una pista para solucionarlo
        print(f"Error conectando a Redis: {e}")
        print("   ¿Ejecutaste 'sudo docker run --rm -d -p 6379:6379 --name redis redis'?")
        return

    # 2. Obtener IP y puerto local
    mi_ip = await get_my_ip()

    loop = asyncio.get_running_loop() # Obtenemos el loop de eventos actual para crear un endpoint UDP
    transport, _ = await loop.create_datagram_endpoint( # Creamos un endpoint UDP con nuestro protocolo de chat
        lambda: ChatProtocol(),
        local_addr=('0.0.0.0', 0)
    )

    mi_puerto = transport.get_extra_info('sockname')[1] # Obtenemos el puerto asignado por el sistema para nuestro socket UDP

    # 3. Registrarse en Redis (JOIN)
    print(f"Registrando {nick} en Redis...")

    existe = await redis_client.hexists("chat:usuarios", nick) # Verificamos si el nick ya existe en Redis

    if existe:
        print(f"Error: El nick '{nick}' ya está en uso")
        transport.close() # Cerramos el socket UDP
        await redis_client.close() # Cerramos la conexión a Redis
        return

    # Guardar en Redis
    await redis_client.hset("chat:usuarios", nick, f"{mi_ip}:{mi_puerto}") 
    print(f"Registrado correctamente como {nick} ({mi_ip}:{mi_puerto})")

    # Mostrar todos los usuarios registrados
    todos = await redis_client.hgetall("chat:usuarios")
    print(f"Usuarios activos: {todos}")

    print("Comandos: /CONNECT <nick> | /QUIT")

    # 4. Iniciar shell interactiva
    try:
        await shell_interactiva(transport, nick, redis_client)
    finally:
        transport.close()
        await redis_client.close() # Cerrar la conexión a Redis al finalizar el chat
        print("Chat finalizado")

# Punto de entrada
if __name__ == "__main__":
    asyncio.run(main())