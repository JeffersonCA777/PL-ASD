import asyncio  # Importamos el módulo asyncio para programación asíncrona
import random # Para generar el número aleatorio que el cliente debe adivinar

HOST = '0.0.0.0' # Escuchar en todas las interfaces de red disponibles
PORT = 8888 # Puerto en el que el servidor escuchará las conexiones entrantes

async def jugar(reader, writer): # Función que maneja la lógica del juego de forma asíncrona

    # 1. Saludo
    writer.write("Bienvenido/a al juego. ¿Cómo te llamas?\n".encode("utf-8"))
    await writer.drain()  # Esperamos a que se envíe el mensaje
    
    # 2. Leer nombre 
    data = await reader.read(1024)  # Leemos el nombre del jugador de forma asíncrona
    nombre = data.decode("utf-8").strip()
    
    # 3. Preparar partida
    numero = random.randint(1, 100) # Pensamos el número aleatorio entre 1 y 100 que el jugador debe adivinar
    intentos = 0
    
    # 4. Mensaje de inicio
    writer.write(f"Hola {nombre}, he pensado un numero entre 1 y 100.\n".encode("utf-8"))
    await writer.drain() # Esperamos a que se envíe el mensaje
    
    # 5. Bucle del juego
    while True:
        writer.write(b"Adivina: ")
        await writer.drain()
        
        # Leer intento
        data = await reader.read(1024) # Leemos la respuesta del jugador de forma asíncrona
        if not data:  # Cliente desconectado
            break
            
        linea = data.decode("utf-8").strip()
        
        try:
            intento = int(linea)
            intentos += 1
            
            if intento < numero: # Intento menor que el número a adivinar
                writer.write("Es mayor\n".encode("utf-8")) 
                await writer.drain()
            elif intento > numero: # Intento mayor que el número a adivinar
                writer.write("Es menor\n".encode("utf-8"))
                await writer.drain()
            else:
                writer.write(f"¡Acertaste, {nombre}! ¡En {intentos} intentos!\n".encode("utf-8")) # Intento correcto
                await writer.drain()
                break
                
        except ValueError: # Si el jugador no introduce un número válido, le pedimos que lo intente de nuevo
            writer.write("Por favor, introduce un numero\n".encode("utf-8"))
            await writer.drain()
    
    # 6. Cerrar la conexión
    writer.close()
    await writer.wait_closed() # Esperamos a que se cierre la conexión

async def main(): # Función principal del servidor

    server = await asyncio.start_server(
        jugar,           # Función que manejará cada cliente conectado
        HOST,            # Dirección IP en la que el servidor escuchará 
        PORT             # Puerto en el que el servidor escuchará
    )
    
    addr = server.sockets[0].getsockname() # Obtenemos la dirección en la que el servidor está escuchando
    print(f"Servidor ASYNCIO escuchando en {addr}")
    
    # Bucle infinito atendiendo clientes
    async with server:
        await server.serve_forever() # Esperamos a que el servidor atienda clientes de forma indefinida

if __name__ == "__main__":
    asyncio.run(main()) # Arrancamos el servidor ejecutando la función main()