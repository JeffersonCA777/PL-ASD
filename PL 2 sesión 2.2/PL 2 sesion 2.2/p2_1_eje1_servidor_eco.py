"""
Ejercicio 1 - Servidor Eco básico
Puerto fijo: 7000
"""

import socket
import sys

def main():
    # 1. Crear el socket (el teléfono del restaurante)
    # AF_INET = IPv4, SOCK_STREAM = TCP
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 2. Asignar dirección y puerto (la dirección del restaurante)
    # '' significa "todas las interfaces de red" (localhost también)
    direccion = ('', 7000)  # Puerto fijo 7000
    
    try:
        servidor.bind(direccion)
        print(f"✅ Servidor escuchando en puerto 7000")
    except Exception as e:
        print(f"❌ Error al bind: {e}")
        sys.exit(1)
    
    # 3. Poner el servidor en modo escucha
    # 5 = número máximo de clientes en cola de espera
    servidor.listen(5)
    print("🔄 Esperando clientes...")
    
    # 4. Bucle principal (el restaurante siempre abierto)
    while True:
        try:
            # Esperar a que llegue un cliente
            cliente_socket, direccion_cliente = servidor.accept()
            print(f"🎉 Cliente conectado desde {direccion_cliente}")
            
            # Bucle para atender a ESTE cliente
            while True:
                # Recibir datos del cliente (máximo 1024 bytes)
                datos = cliente_socket.recv(1024)
                
                # Si recibimos datos vacíos, el cliente cerró la conexión
                if not datos:
                    print(f"👋 Cliente {direccion_cliente} se desconectó")
                    break
                
                # Mostrar lo que recibimos (opcional, para debugging)
                print(f"📨 Recibido: {datos.decode('utf-8').strip()}")
                
                # Enviar los mismos datos de vuelta (ECO)
                cliente_socket.sendall(datos)
                print(f"📤 Enviado eco")
            
            # Cerrar la conexión con este cliente
            cliente_socket.close()
            
        except KeyboardInterrupt:
            print("\n🛑 Servidor detenido por el usuario")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
    
    # Cerrar el socket del servidor
    servidor.close()
    print("👋 Hasta luego!")

if __name__ == "__main__":
    main()