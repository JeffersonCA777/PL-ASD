"""
Ejercicio 5 Opcional: Scraping de videojuegos de Wikipedia
Extrae la lista de videojuegos más vendidos desde Wikipedia.
"""

import json
import re
from lxml import html
from pydantic import BaseModel, ValidationError
import urllib.request

# ============================================================
# PARTE 1: Definir el modelo de datos con Pydantic
# ============================================================

class Videojuego(BaseModel):
    """Modelo que representa un videojuego (Lista de más vendidos)"""
    posicion: int | None = None
    titulo: str
    ventas_millones: float | None = None
    plataforma: str | None = None
    año: int | None = None


# ============================================================
# PARTE 2: Descargar la página con User-Agent
# ============================================================

print(" Descargando página de Wikipedia...")

url = "https://en.wikipedia.org/wiki/List_of_best-selling_video_games"

try:
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    )
    
    u = urllib.request.urlopen(req)
    contenido = u.read()
    u.close()
    
    print(f" Página descargada correctamente ({len(contenido)} bytes)\n")
    
except Exception as e:
    print(f" Error al descargar la página: {e}")
    exit(1)


# ============================================================
# PARTE 3: Parsear el HTML con lxml
# ============================================================

print(" Analizando el HTML...")
arbol = html.fromstring(contenido)


# ============================================================
# PARTE 4: Encontrar la tabla de juegos más vendidos
# ============================================================

# Buscar la tabla que contiene Tetris
tablas = arbol.xpath('//table[contains(., "Tetris") and contains(., "520")]')

if not tablas:
    print(" No se encontró la tabla de juegos más vendidos")
    exit(1)

tabla = tablas[0]
print(" Tabla de juegos más vendidos encontrada\n")

# Obtener las filas de la tabla (excluyendo cabeceras)
filas = tabla.xpath(".//tr[td]")
print(f"🎮 Se encontraron {len(filas)} juegos\n")


# ============================================================
# PARTE 5: Extraer los datos de cada juego
# Basado en la estructura real de la tabla:
# Columna 0: Posición (ej: 1, 2, 3)
# Columna 1: Título (ej: Tetris, Minecraft)
# Columna 2: Ventas (ej: 520, 350, 225)
# Columna 3: Plataforma (ej: Multi-platform, Wii)
# Columna 4: Año (ej: 1988, 2011, 2013)
# ============================================================

lista_juegos = []
errores = 0

for i, fila in enumerate(filas, 1):
    print(f" Procesando juego {i} de {len(filas)}...")
    
    celdas = fila.xpath(".//td")
    
    # --- Posición (columna 0) ---
    posicion = None
    if len(celdas) > 0:
        posicion_elem = celdas[0].xpath(".//text()")
        if posicion_elem:
            try:
                posicion = int(posicion_elem[0].strip())
            except (ValueError, AttributeError):
                posicion = None
    
    # --- Título (columna 1) ---
    titulo = "Sin título"
    if len(celdas) > 1:
        # Buscar enlaces primero (son los títulos)
        titulo_elem = celdas[1].xpath(".//a/text()")
        if titulo_elem:
            titulo = titulo_elem[0].strip()
        else:
            # Si no hay enlace, tomar texto directo
            titulo_elem = celdas[1].xpath(".//text()")
            if titulo_elem:
                titulo = titulo_elem[0].strip()
    
    # --- Ventas (columna 2) ---
    ventas_millones = None
    if len(celdas) > 2:
        ventas_elem = celdas[2].xpath(".//text()")
        if ventas_elem:
            ventas_texto = ventas_elem[0].strip()
            # Limpiar: quitar "million", "million+", etc.
            ventas_texto = re.sub(r'[^\d\.]', '', ventas_texto)
            try:
                if ventas_texto:
                    ventas_millones = float(ventas_texto)
            except ValueError:
                ventas_millones = None
    
    # --- Plataforma (columna 3) ---
    plataforma = None
    if len(celdas) > 3:
        plataforma_elem = celdas[3].xpath(".//text()")
        if plataforma_elem:
            plataforma = plataforma_elem[0].strip()
    
    # --- Año (columna 4) ---
    año = None
    if len(celdas) > 4:
        año_elem = celdas[4].xpath(".//text()")
        if año_elem:
            try:
                año = int(año_elem[0].strip())
            except ValueError:
                año = None
    
    print(f"    #{posicion if posicion else '?'}: {titulo[:40]} | Ventas: {ventas_millones if ventas_millones else '?'}M | Plataforma: {plataforma if plataforma else '?'} | Año: {año if año else '?'}")
    
    # ----- Crear objeto Videojuego -----
    try:
        juego = Videojuego(
            posicion=posicion,
            titulo=titulo,
            ventas_millones=ventas_millones,
            plataforma=plataforma,
            año=año
        )
        lista_juegos.append(juego)
        print(f"    Validado correctamente")
    except ValidationError as e:
        print(f"    Error al validar: {e}")
        errores += 1
        continue


# ============================================================
# PARTE 6: Exportar a JSON
# ============================================================

print(f"\n💾 Guardando datos en wikipedia_juegos.json...")

juegos_dict = [juego.model_dump() for juego in lista_juegos]

with open("wikipedia_juegos.json", "w", encoding="utf-8") as f:
    json.dump(juegos_dict, f, indent=2, ensure_ascii=False)

print(f" Datos guardados en wikipedia_juegos.json ({len(juegos_dict)} juegos)")
print(f" Errores encontrados: {errores}")

print("\n Ejercicio 5 Opcional completado!")