import json # Para leer el archivo JSON
from pydantic import BaseModel, ValidationError # Para definir el modelo de datos y validar los datos

# PARTE 1: Definir el modelo de datos (igual que en el ejercicio 2)
class Farmacia(BaseModel): # Definimos un modelo de datos para representar cada farmacia
    nombre: str # El nombre de la farmacia
    direccion: str # La dirección de la farmacia
    codigo_postal: int # El código postal de la farmacia
    telefono: str # El número de teléfono de la farmacia
    poblacion: str # La población donde se encuentra la farmacia
    horario: str # El horario de atención de la farmacia

# PARTE 2: Leer el archivo JSON
print(" Leyendo farmacias.json...")

try:
    with open("farmacias.json", "r", encoding="utf-8") as f: # Abrimos el archivo JSON para lectura
        datos = json.load(f) # Cargamos los datos del archivo JSON 
    print(f" Se leyeron {len(datos)} registros del archivo\n")
except FileNotFoundError:
    print(" Error: No se encuentra el archivo 'farmacias.json'")
    print("   Primero ejecuta el ejercicio 2 para generarlo.")
    exit(1)
except json.JSONDecodeError as e:
    print(f" Error: El archivo JSON no tiene un formato válido: {e}")
    exit(1)

# PARTE 3: Validar los datos con Pydantic
print(" Validando datos con Pydantic...")

lista_farmacias = [] # Lista para almacenar las farmacias válidas
errores = 0 # Contador de errores de validación

for i, item in enumerate(datos, 1): # Iteramos sobre cada registro del JSON
    try:
        # Convertir el diccionario en un objeto Farmacia
        farmacia = Farmacia.model_validate(item)
        lista_farmacias.append(farmacia)
    except ValidationError as e:
        errores += 1
        print(f"    Error en registro {i}: {e}")
        continue

print(f" Validación completada: {len(lista_farmacias)} farmacias válidas")
if errores > 0:
    print(f"    Se encontraron {errores} registros con errores\n")
else:
    print()

# PARTE 4: Buscar farmacias por población

# Pedir al usuario la población a buscar
poblacion_buscar = input(" Introduce una población para buscar farmacias: ").strip().upper()

print(f"\n{'='*50}")
print(f" Buscando farmacias en {poblacion_buscar}...")
print('='*50)

# Buscar farmacias que coincidan
farmacias_encontradas = [] # Lista para almacenar las farmacias que coincidan con la población buscada
for farmacia in lista_farmacias:
    # Convertir a mayúsculas para comparar sin distinguir mayúsculas/minúsculas
    if farmacia.poblacion.upper() == poblacion_buscar: # Si la población de la farmacia coincide con la población buscada
        farmacias_encontradas.append(farmacia) # Agregar la farmacia a la lista de resultados

# Mostrar resultados
if farmacias_encontradas: # Si se encontraron farmacias, mostrar la información de cada una
    print(f"\n Se encontraron {len(farmacias_encontradas)} farmacias:\n")
    for i, farmacia in enumerate(farmacias_encontradas, 1):
        print(f"  {i}. {farmacia.nombre}")
        print(f"      Teléfono: {farmacia.telefono}")
        print(f"      Horario: {farmacia.horario}\n")
else:
    print(f"\n No se encontraron farmacias en {poblacion_buscar}")

print("\n Ejercicio 3 completado!")