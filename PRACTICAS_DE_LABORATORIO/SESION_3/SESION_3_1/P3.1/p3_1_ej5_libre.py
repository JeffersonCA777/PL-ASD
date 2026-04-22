"""
Ejercicio 5 Opcional: Scraping de videojuegos de Wikipedia
Version funcional que extrae 43 juegos.
"""

import scrapy
import re
from pydantic import BaseModel

# 1: Definir un modelo de datos con Pydantic
class Videojuego(BaseModel):
    posicion: int | None = None
    titulo: str
    ventas_millones: float | None = None
    plataforma: str | None = None
    año: int | None = None

# 2: Definir el Spider de Scrapy
class VideojuegosSpider(scrapy.Spider):
    name = "videojuegos_wikipedia"
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'HTTPCACHE_ENABLED': True, # Actvar el cache HTTP para evitar bloqueos por parte de Wikipedia
        'FEEDS': {
            'wikipedia_juegos_scrapy.json': {
                'format': 'json',
                'encoding': 'utf8',
                'indent': 2,
            },
        },
    }
    
    start_urls = [
        "https://en.wikipedia.org/wiki/List_of_best-selling_video_games"
    ]
    
    def limpiar(self, texto):
        if not texto:
            return ""
        texto = re.sub(r'\[\w+\]', '', texto) # Eliminar patrones.
        return texto.strip()
    
    # Metodo principal para extraer los datos de la tabla
    def parse(self, response):
        print("\nExtrayendo datos de Wikipedia...")
        
        # Buscar la tabla que contiene los datos de Tetris
        tabla = response.xpath("//table[contains(., 'Tetris') and contains(., '520')]")
        if not tabla:
            print("No se encontro la tabla")
            return
        
        # Obtener todas las filas de la tabla que tienen datos
        filas = tabla.xpath(".//tr[td]")
        print(f"Total filas: {len(filas)}\n")
        
        # Variables para almacenar datos pendientes
        juegos = []
        titulo_pendiente = None
        plataforma_pendiente = None
        año_pendiente = None
        posicion_pendiente = None
        
        # Recorrer cada fila y extraer los datos
        for i, fila in enumerate(filas, 1):
            celdas = fila.xpath(".//td")
            
            # Extraer texto de cada celda 
            textos = []
            for celda in celdas:
                texto = self.limpiar(celda.xpath(".//text()").get())
                textos.append(texto)
            
            print(f"Fila {i}: {textos[:6]}")
            
            # Patron 1: Fila con titulo en col1 (como Minecraft)
            if len(textos) > 1 and textos[1] and not textos[1].replace('.', '').isdigit():
                titulo_pendiente = textos[1] # Guarda titulo para asociar con ventas.
                posicion_pendiente = int(textos[0]) if textos[0] and textos[0].isdigit() else None
                plataforma_pendiente = textos[2] if len(textos) > 2 else None
                año_pendiente = int(textos[3]) if len(textos) > 3 and textos[3].isdigit() else None
                print(f"   Titulo pendiente: {titulo_pendiente}")
            
            # Patron 2: Fila con ventas en col1 y titulo en col2 (como GTA V)
            elif len(textos) > 1 and textos[1] and textos[1].replace('.', '').isdigit():
                ventas = float(textos[1]) # Extraer ventas.
                posicion = int(textos[0]) if textos[0] and textos[0].isdigit() else None
                titulo = textos[2] if len(textos) > 2 else None
                plataforma = textos[3] if len(textos) > 3 else None
                año = int(textos[4]) if len(textos) > 4 and textos[4].isdigit() else None
                
                # Si no hay un titulo pendiente, lo asociamos con las ventas actuales.
                if titulo_pendiente:
                    juego = Videojuego(
                        posicion=posicion_pendiente or posicion,
                        titulo=titulo_pendiente,
                        ventas_millones=ventas,
                        plataforma=plataforma_pendiente or plataforma,
                        año=año_pendiente or año
                    )
                    print(f"   #{juego.posicion}: {juego.titulo} - {ventas}M - {juego.plataforma} - {juego.año}")
                    juegos.append(juego)
                    # Limpiar variables pendientes
                    titulo_pendiente = None
                    plataforma_pendiente = None
                    año_pendiente = None
                    posicion_pendiente = None
                elif titulo:
                    juego = Videojuego(
                        posicion=posicion,
                        titulo=titulo,
                        ventas_millones=ventas,
                        plataforma=plataforma,
                        año=año
                    )
                    print(f"   #{posicion}: {titulo} - {ventas}M - {plataforma} - {año}")
                    juegos.append(juego)
        
        print(f"\nTotal juegos extraidos: {len(juegos)}")
        
        # Devolver cada juego como diccionario para que Scrappy lo guarde.
        for juego in juegos:
            yield juego.model_dump()

# 3. Punto de partida del programa
if __name__ == "__main__":
    pass