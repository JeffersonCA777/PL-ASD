import asyncio

# CONFIGURACIÓN
HOST = '127.0.0.1'  # Solo localhost (más seguro para pruebas)
PORT = 7000

# 1. FUNCIÓN PARA MANEJAR CADA CLIENTE (CORRUTINA)
async def manejar_cliente(reader, writer):
    """
    reader: para leer datos del cliente
    writer: para escribir datos al cliente
    """
    direccion = writer.get_extra_info('peername')
    print(f"Cliente conectado desde {direccion}")
    
    try:
        while True:
            # Leer datos (esto se PAUSA si no hay datos)
            datos = await reader.read(1024)
            
            if not datos:
                break  # Cliente desconectó
            
            mensaje = datos.decode().strip()
            print(f"Recibido: {mensaje}")
            
            # Enviar eco
            writer.write(datos)
            await writer.drain()  # Asegurar que se envíe
            
            print(f"Enviado eco: {mensaje}")
    
    except asyncio.CancelledError:
        pass
    finally:
        print(f"Cliente {direccion} desconectado")
        writer.close()
        await writer.wait_closed()

# 2. FUNCIÓN PRINCIPAL (CORRUTINA)
async def main():
    # Crear servidor
    servidor = await asyncio.start_server(
        manejar_cliente,  # Función que atiende cada cliente
        HOST,             # Dirección IP
        PORT              # Puerto
    )
    
    print(f"Servidor asyncio escuchando en {HOST}:{PORT}")
    
    # Mantener servidor corriendo (con cierre elegante)
    async with servidor:
        await servidor.serve_forever()

# 3. PUNTO DE ENTRADA
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario")