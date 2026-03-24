import scrapy
import re
from pydantic import BaseModel

class Videojuego(BaseModel):
    posicion: int | None = None
    titulo: str
    ventas_millones: float | None = None
    plataforma: str | None = None
    año: int | None = None


class VideojuegosSpider(scrapy.Spider):
    name = "videojuegos_wikipedia"
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'HTTPCACHE_ENABLED': True,
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
        texto = re.sub(r'\[\w+\]', '', texto)
        return texto.strip()
    
    def parse(self, response):
        print("\n Extrayendo datos de Wikipedia...")
        
        # Encontrar la tabla correcta
        tabla = response.xpath("//table[contains(., 'Tetris') and contains(., '520')]")
        if not tabla:
            print(" No se encontró la tabla")
            return
        
        filas = tabla.xpath(".//tr[td]")
        print(f" Total filas: {len(filas)}\n")
        
        juegos = []
        titulo_pendiente = None
        plataforma_pendiente = None
        año_pendiente = None
        posicion_pendiente = None
        
        for i, fila in enumerate(filas, 1):
            celdas = fila.xpath(".//td")
            
            # Extraer textos de cada celda
            textos = []
            for celda in celdas:
                texto = self.limpiar(celda.xpath(".//text()").get())
                textos.append(texto)
            
            print(f"Fila {i}: {textos[:6]}")
            
            # Determinar tipo de fila basado en el patrón observado
            # Patrón 1: Fila con título en col1 (como Minecraft)
            if len(textos) > 1 and textos[1] and not textos[1].replace('.', '').isdigit():
                # Esta fila contiene un título
                titulo_pendiente = textos[1]
                posicion_pendiente = int(textos[0]) if textos[0] and textos[0].isdigit() else None
                plataforma_pendiente = textos[2] if len(textos) > 2 else None
                año_pendiente = int(textos[3]) if len(textos) > 3 and textos[3].isdigit() else None
                print(f"    Título pendiente: {titulo_pendiente} (pos:{posicion_pendiente})")
            
            # Patrón 2: Fila con ventas en col1 y título en col2 (como GTA V)
            elif len(textos) > 1 and textos[1] and textos[1].replace('.', '').isdigit():
                ventas = float(textos[1])
                posicion = int(textos[0]) if textos[0] and textos[0].isdigit() else None
                titulo = textos[2] if len(textos) > 2 else None
                plataforma = textos[3] if len(textos) > 3 else None
                año = int(textos[4]) if len(textos) > 4 and textos[4].isdigit() else None
                
                # Si tenemos título pendiente, usar esa información
                if titulo_pendiente:
                    juego = Videojuego(
                        posicion=posicion_pendiente or posicion,
                        titulo=titulo_pendiente,
                        ventas_millones=ventas,
                        plataforma=plataforma_pendiente or plataforma,
                        año=año_pendiente or año
                    )
                    print(f"    #{juego.posicion}: {juego.titulo} - {ventas}M - {juego.plataforma} - {juego.año}")
                    juegos.append(juego)
                    # Limpiar pendientes
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
                    print(f"    #{posicion}: {titulo} - {ventas}M - {plataforma} - {año}")
                    juegos.append(juego)
        
        print(f"\ Total juegos extraídos: {len(juegos)}")
        
        for juego in juegos:
            yield juego.model_dump()