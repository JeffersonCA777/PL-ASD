from lxml import etree

# 1. Cargar el archivo XML y parsearlo
print("Cargando datos.xml...")
arbol = etree.parse("datos.xml")
print("Archivo cargado correctamente\n")

# 2. Consulta 1: Número de libros de categoría WEB
print("=" * 50)
print("CONSULTA 1: Libros de categoría WEB")
print("=" * 50)

libros_web = arbol.xpath("//book[@category='WEB']")
print(f" Número de libros de categoría WEB: {len(libros_web)}")

# 3. Consulta 2: Libros con más de un autor
print("\n" + "=" * 50)
print("CONSULTA 2: Libros con más de un autor")
print("=" * 50)

libros_multi_autor = arbol.xpath("//book[count(author) > 1]")

if libros_multi_autor:
    print(f" Se encontraron {len(libros_multi_autor)} libros con más de un autor:\n")
    for i, libro in enumerate(libros_multi_autor, 1):
        titulo = libro.xpath("title/text()")[0] if libro.xpath("title/text()") else "Sin título"
        precio = libro.xpath("price/text()")[0] if libro.xpath("price/text()") else "Sin precio"
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