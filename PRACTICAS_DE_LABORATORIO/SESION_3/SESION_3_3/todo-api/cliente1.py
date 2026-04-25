"""
Cliente 1 para el chat WebSocket.
Este cliente se conecta al chat grupal usando WebSocket.
Se autentica con el usuario testuser y permite enviar y recibir mensajes.
"""

# 1. Importar librerías necesarias
import asyncio
import websockets
import sys
import json
import subprocess

# 2. Función principal del cliente
async def chat():
    # Obtener token para testuser
    result = subprocess.run(
        ["curl", "-s", "-X", "POST", "http://localhost:8000/token",
         "-d", "username=testuser&password=1234"],
        capture_output=True, text=True
    )
    token = json.loads(result.stdout)["access_token"]
    
    # Conectar al WebSocket del chat usando el token
    uri = f"ws://localhost:8000/ws?token={token}"
    async with websockets.connect(uri) as websocket:
        print("Conectado al chat como testuser")
        print("Escribe mensajes. Presiona Ctrl+C para salir.")
        
        # Función para recibir mensajes del chat
        async def recibir():
            try:
                while True:
                    msg = await websocket.recv()
                    print(f"\n[Recibido] {msg}")
                    print("> ", end="", flush=True)
            except:
                pass
        
        # Función para enviar mensajes al chat
        async def enviar():
            loop = asyncio.get_event_loop()
            while True:
                msg = await loop.run_in_executor(None, sys.stdin.readline)
                if msg.strip():
                    await websocket.send(msg.strip())
                    print("> ", end="", flush=True)
        
        await asyncio.gather(recibir(), enviar())

# 3: Punto de entrada del programa
if __name__ == "__main__":
    asyncio.run(chat())
