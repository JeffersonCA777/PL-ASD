"""
Codigo de prueba para verificar la ejecucion de Python dentro de un contenedor Docker.
"""

# 1. Librerias
import sys

# 2. Funcion principal
def main():
    print("Hola mundo!")
    print(f"Soy la versión {sys.version} de Python")

# 3. Punto de entrada del programa
if __name__ == "__main__":
    main()
