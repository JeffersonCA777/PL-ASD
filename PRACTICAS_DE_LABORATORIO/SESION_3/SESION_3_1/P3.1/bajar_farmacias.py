"""
Script para descargar la página de farmacias de guardia de Asturias
y guardarla localmente.
"""

import urllib.request # Importamos el módulo urllib.request para realizar la descarga de la página web

print(" Descargando página de farmacias...")

# URL de la página
url = "http://www.farmasturias.org/GESCOF/cms/Guardias/FarmaciaBuscar.asp?IdMenu=111"

# Abrir la conexión y descargar
u = urllib.request.urlopen(url) # Abrimos la URL y obtenemos un objeto de respuesta que contiene el contenido de la página
contenido = u.read() # Leemos el contenido de la respuesta y lo almacenamos en la variable 'contenido' como bytes
u.close() # Cerramos la conexión para liberar recursos

# Guardar en un archivo local
with open("pagina-farmacias.html", "wb") as f: # Abrimos un archivo en modo escritura binaria para guardar el contenido descargado
    f.write(contenido) # Escribimos el contenido descargado en el archivo local

print(" Página guardada como 'pagina-farmacias.html'")
print(f" Tamaño del archivo: {len(contenido)} bytes")