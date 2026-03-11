import asyncio # Biblioteca para programación asíncrona
import sys # Biblioteca para leer argumentos y manejar entrada/salida

class ChatProtocol(asyncio.DatagramProtocol): # Esta clase maneja los mensajes que recibimos
    
    def datagram_received(self, data, addr): #Cuando llega un mensaje, esto se ejecuta automáticamente
        mensaje = data.decode('utf-8').strip() # Convertir bytes a string y eliminar espacios
        print(f"\n{mensaje}")
        print("> ", end="", flush=True)

async def leer_teclado(): # Conecta el teclado al sistema para leer sin bloquear
    reader = asyncio.StreamReader() # Crear un lector de flujo asíncrono
    protocol = asyncio.StreamReaderProtocol(reader) # Protocolo que conecta el lector al sistema de eventos
    loop = asyncio.get_running_loop()
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    return reader

async def shell_interactivo(transport, nick): # Función que maneja la interacción con el usuario (ASÍNCRONA)
    reader = await leer_teclado() # Esperar a que el usuario escriba algo en el teclado
    destino = None  # Aquí guardaremos a quién le escribimos
    
    print(f"=== CHAT INICIADO ===")
    print(f"Tu nick: {nick}")
    print("Comandos: /CONNECT <ip> <puerto> | /QUIT")
    
    while True:
        print("> ", end="", flush=True)
        linea = await reader.readline() # Esperar a que el usuario escriba una línea y presione Enter
        texto = linea.decode('utf-8').strip() 
        
        if texto.startswith("/QUIT"): # Si el usuario quiere salir
            print("¡Hasta luego!")
            break
            
        elif texto.startswith("/CONNECT"): # Si el usuario quiere conectar a alguien
            partes = texto.split()
            if len(partes) == 3: # /CONNECT <ip> <puerto>
                ip = partes[1]
                puerto = int(partes[2])
                destino = (ip, puerto)
                print(f"✓ Ahora envías mensajes a {ip}:{puerto}")
            else:
                print("✗ Uso: /CONNECT <ip> <puerto>")
        
        elif destino:  # Si tenemos un destino configurado
            mensaje = f"{nick}> {texto}"
            transport.sendto(mensaje.encode('utf-8'), destino) # Enviar el mensaje al destino configurado
        else:
            print("✗ Primero usa /CONNECT para establecer destino")

async def main(): # Función principal
    if len(sys.argv) != 3: # Verificar que se hayan pasado los argumentos necesarios
        print("Uso: python3 p2_5_ej1_chat_async.py <nick> <puerto>")
        return
    
    nick = sys.argv[1] # El primer argumento es el nick del usuario
    puerto_local = int(sys.argv[2]) # El segundo argumento es el puerto local donde escucharemos los mensajes entrantes
    
    loop = asyncio.get_running_loop() # Obtener el bucle de eventos actual
    transport, _ = await loop.create_datagram_endpoint( # Crear un endpoint UDP para escuchar mensajes entrantes
        ChatProtocol,
        local_addr=('0.0.0.0', puerto_local)
    )
    
    print(f"Escuchando en puerto {puerto_local}")
    await shell_interactivo(transport, nick) # Iniciar la shell interactiva para enviar mensajes
    transport.close()

if __name__ == "__main__": # Punto de entrada del programa
    asyncio.run(main()) # Ejecutar la función principal en el bucle de eventos asíncrono