import asyncio # Biblioteca para programación asíncrona
import sys     # Biblioteca para leer argumentos y manejar entrada/salida

registros = {}  # Diccionario compartido (igual que en Ejercicio 2)

async def manejar_cliente(reader, writer): # Función que atiende a cada cliente (ASÍNCRONA)
    addr = writer.get_extra_info('peername') # Información del cliente
    print(f"Cliente conectado desde {addr}")

    try:
        data = await reader.read(1024) # Leer datos del cliente
        if not data:
            return # Si no se recibe nada, cerrar conexión

        mensaje = data.decode().strip() # Convertir bytes a string
        print(f"Recibido: {mensaje}")

        partes = mensaje.split() # Separar comando y argumentos
        comando = partes[0] if partes else "" 
        respuesta = ""

        if comando == "JOIN" and len(partes) == 4: # JOIN <nick> <ip> <puerto>
            _, nick, ip, puerto_str = partes
            try:
                puerto = int(puerto_str) # Validar que el puerto es un número
                if nick in registros:
                    respuesta = "ERROR\n"
                    print(f"  → {nick} YA EXISTE")
                else:
                    registros[nick] = (ip, puerto) # Guardar registro
                    respuesta = "OK\n"
                    print(f"  → Registrado {nick} = ({ip}, {puerto})")
                    print(f"  → Diccionario: {registros}")
            except ValueError:
                respuesta = "ERROR\n"

        elif comando == "LEAVE" and len(partes) == 2: # LEAVE <nick>
            _, nick = partes
            if nick in registros:
                del registros[nick]
                respuesta = "OK\n"
                print(f"  → Eliminado {nick}")
                print(f"  → Diccionario: {registros}")
            else:
                respuesta = "ERROR\n"

        elif comando == "QUERY" and len(partes) == 2: # QUERY <nick>
            _, nick = partes
            if nick in registros:
                ip, puerto = registros[nick]
                respuesta = f"OK {ip} {puerto}\n"
                print(f"  → QUERY {nick}: encontrado {ip}:{puerto}")
            else:
                respuesta = "ERROR\n" # Respuesta de error para QUERY si no se encuentra
                print(f"  → QUERY {nick}: NO encontrado")

        else: # Comando no reconocido o formato incorrecto
            respuesta = "ERROR\n"
            print(f"  → Comando inválido: {mensaje}")

        writer.write(respuesta.encode()) # Enviar respuesta al cliente
        await writer.drain()  # Asegurar que se envíe antes de continuar

    except Exception as e:
        print(f"Error con cliente {addr}: {e}")
    finally:
        writer.close() # Cerrar conexión con el cliente
        await writer.wait_closed() # Esperar a que se cierre completamente
        print(f"Cliente {addr} desconectado")


async def main(): # Función principal del servidor
    HOST = '0.0.0.0' # Escuchar en todas las interfaces
    PORT = 11111 # Puerto del broker

    servidor = await asyncio.start_server( # Crear servidor TCP asíncrono
        manejar_cliente,    # Función que atiende cada cliente
        HOST,               # IP de escucha
        PORT                # Puerto
    )

    print(f"Broker ASÍNCRONO escuchando en {HOST}:{PORT}")
    print("Protocolo: JOIN/LEAVE/QUERY")
    print("Presiona Ctrl+C para detener")
    print("=" * 50) # Separador visual en la consola

    async with servidor: # Mantener el servidor activo
        await servidor.serve_forever() # Esperar hasta que se interrumpa (Ctrl+C)

if __name__ == "__main__": # Punto de entrada del programa
    try:
        asyncio.run(main()) # Ejecutar la función principal del servidor
    except KeyboardInterrupt: # Manejar interrupción por Ctrl+C para cerrar el servidor
        print("\n Broker detenido por el usuario")