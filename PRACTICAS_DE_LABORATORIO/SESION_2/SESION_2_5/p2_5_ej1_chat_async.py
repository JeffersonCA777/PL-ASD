import asyncio
import sys

class ChatProtocol(asyncio.DatagramProtocol):
    """Esta clase maneja los mensajes que recibimos"""
    
    def datagram_received(self, data, addr):
        """Cuando llega un mensaje, esto se ejecuta automáticamente"""
        mensaje = data.decode('utf-8').strip()
        print(f"\n{mensaje}")
        print("> ", end="", flush=True)

async def leer_teclado():
    """Conecta el teclado al sistema para leer sin bloquear"""
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    loop = asyncio.get_running_loop()
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    return reader

async def shell_interactivo(transport, nick):
    """El menú principal del programa"""
    reader = await leer_teclado()
    destino = None  # Aquí guardaremos a quién le escribimos
    
    print(f"=== CHAT INICIADO ===")
    print(f"Tu nick: {nick}")
    print("Comandos: /CONNECT <ip> <puerto> | /QUIT")
    
    while True:
        print("> ", end="", flush=True)
        linea = await reader.readline()
        texto = linea.decode('utf-8').strip()
        
        if texto.startswith("/QUIT"):
            print("¡Hasta luego!")
            break
            
        elif texto.startswith("/CONNECT"):
            partes = texto.split()
            if len(partes) == 3:
                ip = partes[1]
                puerto = int(partes[2])
                destino = (ip, puerto)
                print(f"✓ Ahora envías mensajes a {ip}:{puerto}")
            else:
                print("✗ Uso: /CONNECT <ip> <puerto>")
        
        elif destino:  # Si tenemos un destino configurado
            mensaje = f"{nick}> {texto}"
            transport.sendto(mensaje.encode('utf-8'), destino)
        
        else:
            print("✗ Primero usa /CONNECT para establecer destino")

async def main():
    """Función principal"""
    if len(sys.argv) != 3:
        print("Uso: python3 p2_5_ej1_chat_async.py <nick> <puerto>")
        return
    
    nick = sys.argv[1]
    puerto_local = int(sys.argv[2])
    
    # Configurar el socket UDP
    loop = asyncio.get_running_loop()
    transport, _ = await loop.create_datagram_endpoint(
        ChatProtocol,
        local_addr=('0.0.0.0', puerto_local)
    )
    
    print(f"Escuchando en puerto {puerto_local}")
    await shell_interactivo(transport, nick)
    transport.close()

if __name__ == "__main__":
    asyncio.run(main())