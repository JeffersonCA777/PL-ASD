from lxml import etree # Importamos la biblioteca lxml para trabajar con XML y XPath

# 1. Cargar el archivo XML y parsearlo
print("Cargando datos.xml...")
arbol = etree.parse("datos.xml") # Cargamos el archivo XML y lo parseamos para crear un árbol de elementos
print("Archivo cargado correctamente\n")

# 2. Consulta 1: Número de libros de categoría WEB
print("=" * 50)
print("CONSULTA 1: Libros de categoría WEB")
print("=" * 50)

libros_web = arbol.xpath("//book[@category='WEB']") # Utilizamos XPath para seleccionar todos los elementos <book> que tienen un atributo category con el valor "WEB"
print(f" Número de libros de categoría WEB: {len(libros_web)}")

# 3. Consulta 2: Libros con más de un autor
print("\n" + "=" * 50)
print("CONSULTA 2: Libros con más de un autor")
print("=" * 50)

libros_multi_autor = arbol.xpath("//book[count(author) > 1]") # Utilizamos XPath para seleccionar todos los elementos <book> que tienen más de un elemento <author>

if libros_multi_autor:
    print(f" Se encontraron {len(libros_multi_autor)} libros con más de un autor:\n") # Si se encontraron libros con más de un autor, los listamos mostrando su título y precio
    for i, libro in enumerate(libros_multi_autor, 1):
        titulo = libro.xpath("title/text()")[0] if libro.xpath("title/text()") else "Sin título" # Obtenemos el título del libro, si no existe mostramos "Sin título"
        precio = libro.xpath("price/text()")[0] if libro.xpath("price/text()") else "Sin precio" #
        print(f"  {i}. {titulo} - {precio} €")
else:
    print("No se encontraron libros con más de un autor.")

# 4. Consulta 3: Precio total de todos los libros
print("\n" + "=" * 50)
print("CONSULTA 3: Precio total de todos los libros")
print("=" * 50)

precio_total = arbol.xpath("sum(//price)")
print(f" Precio total de todos los libros: {precio_total} €")

print("\n Ejercicio completado!")