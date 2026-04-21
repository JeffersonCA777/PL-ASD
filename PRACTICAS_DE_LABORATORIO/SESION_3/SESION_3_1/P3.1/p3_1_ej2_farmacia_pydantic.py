"""
Ejercicio 2: Scraping de farmacias con lxml y Pydantic
En este sefundo ejercicio se realiza scraping de la pagina web del Colegio de Farmaceuticos
de Asturias para extraer informacion. 

Estos datos se validan usando Pydantic y se exportan a un archivo JSON.
"""

import json # Importamos la biblioteca json para trabajar con archivos JSON
from lxml import html # Importamos la biblioteca lxml para trabajar con HTML y XPath
from pydantic import BaseModel, ValidationError # Importamos para definir modelos de datos y manejar errores de validación

# 1: Definir el modelo de datos con Pydantic

class Farmacia(BaseModel): # Definimos una clase Farmacia que hereda de BaseModel de Pydantic para validar los datos de cada farmacia
    nombre: str # El nombre de la farmacia
    direccion: str # La dirección de la farmacia
    codigo_postal: int # El código postal de la farmacia, extraído de la dirección
    telefono: str # El teléfono de la farmacia
    poblacion: str # La población donde se encuentra la farmacia, extraída usando XPath con preceding::
    horario: str # El horario de la farmacia, extraído usando XPath con preceding::

# 2: Cargar el HTML y parsearlo

print(" Cargando pagina-farmacias.html...")
with open("pagina-farmacias.html", "rb") as f: # Abrimos el archivo HTML en modo lectura binaria para cargarlo
    arbol = html.parse(f) # Parseamos el archivo HTML para crear un árbol de elementos que podemos consultar con XPath
print(" HTML cargado correctamente\n")

# 3: Seleccionar todas las farmacias

print(" Buscando farmacias...")
farmacias_nodos = arbol.xpath("//ul[@class='ListadoResultados']") # Utilizamos XPath para seleccionar todos los elementos <ul>
print(f" Se encontraron {len(farmacias_nodos)} farmacias\n")

# 4: Extraer los datos de cada farmacia

lista_farmacias = [] # Creamos una lista vacía para almacenar los objetos Farmacia que vamos a crear a partir de los datos extraídos

for i, nodo in enumerate(farmacias_nodos, 1): 
    print(f" Procesando farmacia {i} de {len(farmacias_nodos)}...")
    
    # 4.1 Extraer nombre 
    nombre_elem = nodo.xpath(".//span[@class='TituloResultado']/text()") # Utilizamos XPath para seleccionar el texto del elemento <span> con clase "TituloResultado" que contiene el nombre de la farmacia
    nombre = nombre_elem[0].strip() if nombre_elem else "Sin nombre" # Si se encontró el nombre, lo limpiamos con strip() para quitar espacios, si no se encontró mostramos "Sin nombre"
    
    # 4.2 Extraer dirección 
    direccion_elem = nodo.xpath(".//span[@class='ico-localizacion']/text()") # Utilizamos XPath para seleccionar el texto del elemento <span> con clase "ico-localizacion" que contiene la dirección de la farmacia
    if direccion_elem:
        # Limpiar: quitar "Direccion: " del principio
        direccion_raw = direccion_elem[0].replace("Direccion:&nbsp;", "").replace("Direccion: ", "")
        direccion = direccion_raw.strip()
    else:
        direccion = "Sin dirección"
    
    # 4.3 Extraer código postal (de la dirección)
    codigo_postal = 0 # Inicializamos el código postal a 0 por defecto
    if "-" in direccion:
        try:
            cp_str = direccion.split("-")[-1].strip() # Suponemos que el código postal está al final de la dirección después de un guion, lo extraemos y limpiamos
            codigo_postal = int(cp_str) # Intentamos convertir el código postal a entero, si no es un número válido se lanzará una excepción
        except ValueError:
            codigo_postal = 0
    
    # 4.4 Extraer teléfono 
    telefono_elem = nodo.xpath(".//span[@class='ico-telefono']/text()") # Utilizamos XPath para seleccionar el texto del elemento <span> con clase "ico-telefono" que contiene el teléfono de la farmacia
    if telefono_elem:
        # Limpiar: quitar "Teléfono: " del principio
        telefono_raw = telefono_elem[0].replace("Teléfono:&nbsp;", "").replace("Teléfono: ", "")
        telefono = telefono_raw.strip()
    else:
        telefono = "Sin teléfono"
    
    # 4.5 Extraer población
    poblacion_elem = nodo.xpath("preceding::h6[@class='LocalidadGuardias']/text()") # Utilizamos XPath con preceding:: para buscar hacia atrás el primer elemento <h6> con clase "LocalidadGuardias" que contiene la población de la farmacia
    if poblacion_elem:
        poblacion = poblacion_elem[-1].strip()  # El último es el más cercano
    else:
        poblacion = "Sin población"
    
    # 4.6 Extraer horario (usando preceding::)
    horario_elem = nodo.xpath("preceding::h5[@class='HorarioGuardias']/a/text()")
    if horario_elem:
        horario = horario_elem[-1].strip()  # El último es el más cercano
    else:
        horario = "Sin horario"
    
    # 4.7 Crear objeto Farmacia con Pydantic
    try:
        farmacia = Farmacia(
            nombre=nombre,
            direccion=direccion,
            codigo_postal=codigo_postal,
            telefono=telefono,
            poblacion=poblacion,
            horario=horario
        )
        lista_farmacias.append(farmacia)
        print(f"    {nombre} - {poblacion}")
    except ValidationError as e:
        print(f"    Error al validar farmacia {i}: {e}")
        continue

print(f"\n Se procesaron {len(lista_farmacias)} farmacias correctamente")

# 5: Exportar a JSON

print("\n Guardando datos en farmacias.json...")

# Convertir cada objeto Farmacia a diccionario
farmacias_dict = [f.model_dump() for f in lista_farmacias]

# Guardar en archivo JSON
with open("farmacias.json", "w", encoding="utf-8") as f:
    json.dump(farmacias_dict, f, indent=2, ensure_ascii=False)

print(f" Datos guardados en farmacias.json ({len(farmacias_dict)} farmacias)")

print("\n Ejercicio 2 completado")

# 6. Punto de entrada del programa
if __name__ == "__main__":
    pass