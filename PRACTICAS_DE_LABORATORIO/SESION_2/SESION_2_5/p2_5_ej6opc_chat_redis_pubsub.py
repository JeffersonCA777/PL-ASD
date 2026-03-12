import asyncio # Biblioteca para programación asíncrona
import sys # Biblioteca para acceder a argumentos de línea de comandos
from redis.asyncio import Redis # Redis asíncrono para Python

class ChatProtocol(asyncio.DatagramProtocol): # Protocolo para manejar mensajes UDP
    def datagram_received(self, data, addr):
        mensaje = data.decode()
        print(f"\n{mensaje}")
        print("> ", end="", flush=True)

async def get_my_ip(): # Función get_my_ip para obtener la IP local
    reader, writer = await asyncio.open_connection("8.8.8.8", 53) # Conexión a un servidor DNS público 
    ip_local = writer.get_extra_info('sockname')[0] # Obtener la IP local desde la conexión
    writer.close()
    return ip_local

async def escuchar_eventos(ps): # Función para escuchar eventos de Redis Pub/Sub
    async for mensaje in ps.listen(): 
        if mensaje['type'] == 'message': # Mensaje recibido en el canal
            print(f"\n[INFO] {mensaje['data']}")
            print("> ", end="", flush=True)

async def shell_interactiva(transport, nick, redis_client, ps): # Función para manejar la shell interactiva del chat
    reader = asyncio.StreamReader() # Crear un StreamReader para leer la entrada del usuario
    protocol = asyncio.StreamReaderProtocol(reader) # Protocolo para manejar la lectura de la entrada estándar
    loop = asyncio.get_running_loop() # Obtener el loop de eventos actual
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    destino = None  # (IP, puerto) del destinatario actual

    while True:
        print("> ", end="", flush=True)
        linea_bytes = await reader.readline() # Leer una línea de la entrada estándar
        if not linea_bytes:
            break

        linea = linea_bytes.decode().strip() # Decodificar y limpiar la línea de entrada

        if not linea:
            continue

        if linea.startswith("/QUIT"): # Comando para salir del chat
            await redis_client.publish("chat:eventos", f"{nick} salió del chat") # Publicar evento de salida
            await redis_client.hdel("chat:usuarios", nick) # Eliminar el usuario del hash de Redis
            print("¡Saliendo...!")
            break

        elif linea.startswith("/CONNECT"): # Comando para conectar con otro usuario
            partes = linea.split() 
            if len(partes) == 2:
                nick_buscar = partes[1]

                valor = await redis_client.hget("chat:usuarios", nick_buscar) # Buscar el usuario en Redis

                if valor:
                    ip, puerto_str = valor.split(':')
                    destino = (ip, int(puerto_str)) # Establecer el destino para enviar mensajes
                    print(f"Conectado a {nick_buscar} en {ip}:{puerto_str}")
                else:
                    print(f"Error: Usuario '{nick_buscar}' no encontrado")
            else:
                print("Uso: /CONNECT <nick>")

        else: # Enviar mensaje al destino actual
            if destino is None:
                print("Error: No has establecido un destino. Usa /CONNECT <nick>")
            else:
                mensaje = f"{nick}> {linea}"
                transport.sendto(mensaje.encode(), destino)

async def main(): # Función principal del programa
    if len(sys.argv) != 2:
        print("Uso: python3 p2_5_ej6opc_chat_redis_pubsub.py <nick>")
        print("(Redis debe estar corriendo en localhost:6379)")
        return

    nick = sys.argv[1]

    try: # 1. Conectar a Redis
        redis_client = Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )
        await redis_client.ping()
        print("Conectado a Redis")
    except Exception as e:
        print(f"Error conectando a Redis: {e}")
        return

    pubsub = redis_client.pubsub() # 2. Suscribirse al canal de eventos
    await pubsub.subscribe("chat:eventos")
    print("Suscrito al canal de eventos")

    asyncio.create_task(escuchar_eventos(pubsub)) # Lanzar tarea para escuchar eventos de Redis 

    mi_ip = await get_my_ip() # 3. Obtener IP local y configurar socket UDP

    loop = asyncio.get_running_loop() # Obtener el loop de eventos actual para crear un socket UDP
    transport, _ = await loop.create_datagram_endpoint( # Crear un socket UDP para enviar y recibir mensajes
        lambda: ChatProtocol(),
        local_addr=('0.0.0.0', 0) # Puerto 0 para asignar uno dinámicamente
    )

    mi_puerto = transport.get_extra_info('sockname')[1]

    print(f"Registrando {nick} en Redis...") # 4. Registrar el usuario en Redis y verificar que no exista otro con el mismo nick

    existe = await redis_client.hexists("chat:usuarios", nick) # Verificar si el nick ya existe en Redis

    if existe:
        print(f"Error: El nick '{nick}' ya está en uso")
        transport.close()
        await redis_client.close() # Cerrar la conexión a Redis
        return

    await redis_client.hset("chat:usuarios", nick, f"{mi_ip}:{mi_puerto}") # Guardar el usuario en Redis con su IP y puerto
    print(f"Registrado correctamente como {nick} ({mi_ip}:{mi_puerto})")

    await redis_client.publish("chat:eventos", f"{nick} ingresó al chat") # Publicar evento de entrada al chat

    todos = await redis_client.hgetall("chat:usuarios") # Mostrar todos los usuarios activos en el chat
    print(f" Usuarios activos: {todos}")

    print("Comandos: /CONNECT <nick> | /QUIT")
    print("Los eventos de entrada/salida se mostrarán automáticamente")

    try: # 5. Iniciar la shell interactiva para enviar mensajes
        await shell_interactiva(transport, nick, redis_client, pubsub)
    finally:
        transport.close() # Cerrar el socket UDP al finalizar
        await redis_client.close() # Cerrar la conexión a Redis al finalizar
        print("Chat finalizado")

if __name__ == "__main__": # Ejecutar la función principal usando asyncio
    asyncio.run(main())