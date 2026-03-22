import urllib.request
from lxml import html

print(" Conectando a Wikipedia...")

req = urllib.request.Request(
    'https://en.wikipedia.org/wiki/List_of_best-selling_video_games',
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
)

contenido = urllib.request.urlopen(req).read()
arbol = html.fromstring(contenido)

# Buscar la tabla que contiene 'Tetris' y '520'
tablas = arbol.xpath('//table[contains(., "Tetris") and contains(., "520")]')

if tablas:
    print(f' Se encontró la tabla correcta')
    tabla = tablas[0]
    cabeceras = tabla.xpath('.//th//text()')
    print(f'Cabeceras: {[c.strip() for c in cabeceras if c.strip()][:8]}')
    print()
    
    # Extraer primeras filas
    filas = tabla.xpath('.//tr[td]')[:5]
    for i, fila in enumerate(filas, 1):
        celdas = fila.xpath('.//td')
        print(f' Fila {i}:')
        for j, celda in enumerate(celdas[:6]):
            texto = celda.xpath('.//text()')
            valor = texto[0].strip() if texto else ''
            print(f'   Columna {j}: {valor}')
        print()
else:
    print(' No se encontró la tabla con Tetris y 520')
    print('Buscando todas las tablas...')
    
    tablas_todas = arbol.xpath('//table[contains(@class, "wikitable")]')
    print(f'Se encontraron {len(tablas_todas)} tablas con clase wikitable')
    
    for i, tabla in enumerate(tablas_todas, 1):
        cabeceras = tabla.xpath('.//th//text()')
        cabeceras_clean = [c.strip() for c in cabeceras if c.strip()][:5]
        print(f'Tabla {i}: {cabeceras_clean}')