# Importaciones
import asyncio  # Para programación asíncrona
import sys  # Para acceder a argumentos de línea de comandos


class ChatProtocol(asyncio.DatagramProtocol):
    """Esta clase maneja los mensajes que recibimos por UDP"""

    def datagram_received(self, data, addr):
        """Este método se llama automáticamente cuando llega un mensaje UDP"""
        mensaje = data.decode()  # Convertir bytes a string (UTF-8)
        print(f"\n{mensaje}")  # Mostrar el mensaje recibido
        print("> ", end="", flush=True)  # Volver a mostrar el prompt


async def get_my_ip():
    """Función para obtener la IP local real del dispositivo"""
    # Conectarse a Google DNS (8.8.8.8 puerto 53) para que el SO asigne una IP local
    reader, writer = await asyncio.open_connection("8.8.8.8", 53)
    ip_local = writer.get_extra_info('sockname')[0]  # Obtener la IP local de la conexión
    writer.close()  # Cerrar la conexión (no necesitamos enviar nada)
    return ip_local  # Devolver la IP local


async def consultar_broker(ip_broker, comando):
    """Envía un comando TCP al broker y devuelve la respuesta"""
    # Conectarse al broker en su IP y puerto 11111
    reader, writer = await asyncio.open_connection(ip_broker, 11111)

    # Enviar el comando (añadiendo \n al final como requiere el protocolo)
    writer.write((comando + "\n").encode())
    await writer.drain()  # Asegurar que los datos se envían

    # Leer la respuesta del broker (máximo 1024 bytes)
    respuesta = await reader.read(1024)

    writer.close()  # Cerrar la conexión TCP
    return respuesta.decode().strip()  # Devolver respuesta como string limpio


async def shell_interactiva(transport, nick, ip_broker):
    """Maneja la interacción con el usuario (teclado)"""
    # === CONFIGURAR LECTURA ASÍNCRONA DEL TECLADO (RECETA MÁGICA) ===
    reader = asyncio.StreamReader()  # Buffer donde se depositará lo que escriba el usuario
    protocol = asyncio.StreamReaderProtocol(reader)  # Protocolo que conecta el teclado con el buffer
    loop = asyncio.get_running_loop()  # Obtener el bucle de eventos actual
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)  # Conectar el teclado al bucle de eventos
    # ================================================================

    destino = None  # Variable que guarda (IP, puerto) del destinatario actual

    while True:  # Bucle principal del chat
        # Mostrar prompt
        print("> ", end="", flush=True)

        # Leer una línea del teclado (NO BLOQUEANTE)
        linea_bytes = await reader.readline()
        if not linea_bytes:  # Si no hay datos (Ctrl+D), salir
            break

        linea = linea_bytes.decode().strip()  # Convertir bytes a string y limpiar

        if not linea:  # Si la línea está vacía, seguir esperando
            continue

        # === PROCESAR COMANDOS ===
        if linea.startswith("/QUIT"):
            # Antes de salir, dar de baja en el broker
            await consultar_broker(ip_broker, f"LEAVE {nick}")
            print("¡Saliendo...!")
            break

        elif linea.startswith("/CONNECT"):
            partes = linea.split()  # Dividir: ["/CONNECT", "Laura"]
            if len(partes) == 2:  # Formato correcto
                nick_buscar = partes[1]  # El nick que queremos buscar

                # Preguntar al broker por la dirección de ese nick
                respuesta = await consultar_broker(ip_broker, f"QUERY {nick_buscar}")

                if respuesta.startswith("OK"):  # El broker tiene al usuario
                    # Formato respuesta: "OK IP PUERTO"
                    _, ip, puerto_str = respuesta.split()
                    destino = (ip, int(puerto_str))  # Guardar como tupla (IP, puerto)
                    print(f"Conectado a {nick_buscar} en {ip}:{puerto_str}")
                else:
                    print(f"Error: Usuario '{nick_buscar}' no encontrado en el broker")
            else:
                print("Uso: /CONNECT <nick>")

        else:  # Es un mensaje normal (no es comando)
            if destino is None:  # Si no hay destinatario configurado
                print("Error: No has establecido un destino. Usa /CONNECT <nick> para conectarte a alguien.")
            else:  # Hay destinatario, enviamos el mensaje
                mensaje = f"{nick}> {linea}"  # Formato: "Laura> Hola"
                transport.sendto(mensaje.encode(), destino)  # Enviar por UDP


async def main():
    """Función principal del programa"""
    # Verificar argumentos de línea de comandos
    if len(sys.argv) != 3:
        print("Uso: python3 p2_5_ej4_chat_con_broker.py <nick> <ip_broker>")
        return

    nick = sys.argv[1]  # Ej: "Laura"
    ip_broker = sys.argv[2]  # Ej: "127.0.0.1" o "192.168.1.10"

    # Obtener nuestra IP local real
    mi_ip = await get_my_ip()

    # Obtener el bucle de eventos
    loop = asyncio.get_running_loop()

    # Crear socket UDP con puerto automático (0 = el SO asigna uno)
    transport, _ = await loop.create_datagram_endpoint(
        lambda: ChatProtocol(),  # Nuestra clase para manejar mensajes entrantes
        local_addr=('0.0.0.0', 0)  # Escuchar en todas las interfaces, puerto automático
    )

    # Obtener el puerto que nos asignó el sistema operativo
    mi_puerto = transport.get_extra_info('sockname')[1]

    # === REGISTRARSE EN EL BROKER ===
    print(f"Registrando {nick} en el broker...")
    respuesta = await consultar_broker(
        ip_broker,
        f"JOIN {nick} {mi_ip} {mi_puerto}"  # Ej: "JOIN Laura 192.168.1.100 54321"
    )

    # Verificar si el registro fue exitoso
    if respuesta != "OK":
        print(f"Error: No se pudo registrar. El nick '{nick}' probablemente ya esté en uso.")
        transport.close()  # Liberar el socket UDP
        return

    # Registro exitoso
    print(f"Registrado correctamente como {nick} ({mi_ip}:{mi_puerto})")
    print("Comandos: /CONNECT <nick> | /QUIT")

    # === INICIAR LA SHELL INTERACTIVA ===
    try:
        await shell_interactiva(transport, nick, ip_broker)
    finally:
        # Al salir (por /QUIT o error), cerrar el transporte
        transport.close()
        print("Chat finalizado")


# Punto de entrada del programa
if __name__ == "__main__":
    asyncio.run(main())  # Arrancar el bucle de eventos de asyncio