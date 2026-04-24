"""
Cliente 2 para el chat WebSocket.
"""

import asyncio
import websockets
import sys
import json
import subprocess

async def chat():
    # Obtener token para maria
    result = subprocess.run(
        ["curl", "-s", "-X", "POST", "http://localhost:8000/token",
         "-d", "username=maria&password=5678"],
        capture_output=True, text=True
    )
    token = json.loads(result.stdout)["access_token"]
    
    uri = f"ws://localhost:8000/ws?token={token}"
    async with websockets.connect(uri) as websocket:
        print("Conectado al chat como maria")
        print("Escribe mensajes. Presiona Ctrl+C para salir.")
        
        async def recibir():
            try:
                while True:
                    msg = await websocket.recv()
                    print(f"\n[Recibido] {msg}")
                    print("> ", end="", flush=True)
            except:
                pass
        
        async def enviar():
            loop = asyncio.get_event_loop()
            while True:
                msg = await loop.run_in_executor(None, sys.stdin.readline)
                if msg.strip():
                    await websocket.send(msg.strip())
                    print("> ", end="", flush=True)
        
        await asyncio.gather(recibir(), enviar())

if __name__ == "__main__":
    asyncio.run(chat())
