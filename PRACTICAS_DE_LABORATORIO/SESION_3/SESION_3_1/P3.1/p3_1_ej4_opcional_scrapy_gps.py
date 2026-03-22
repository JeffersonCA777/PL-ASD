import re # Para expresiones regulares
import scrapy # Para el framework de scraping
from pydantic import BaseModel, ValidationError # Para definir el modelo de datos y validar los resultados

# PARTE 1: Definir el modelo de datos
class Farmacia(BaseModel):
    """Modelo que representa una farmacia con todos sus campos"""
    nombre: str # Nombre de la farmacia
    direccion: str # Dirección completa
    codigo_postal: int  # Código postal 
    telefono: str # Teléfono de contacto
    poblacion: str  # Población donde se encuentra la farmacia
    horario: str # Horario de guardia
    latitud: float | None = None      # Puede ser None si no se encuentra
    longitud: float | None = None     # Puede ser None si no se encuentra

# PARTE 2: Definir el Spider con seguimiento de enlaces
class FarmaciaGPSSpider(scrapy.Spider): # El nombre de la clase es FarmaciaGPSSpider y hereda de scrapy.Spider
    """Spider que extrae farmacias y sus coordenadas GPS"""
    # Nombre único del spider
    name = "farmacias_gps"
    # Configuración personalizada
    custom_settings = {
        'HTTPCACHE_ENABLED': True,           # Activar caché (IMPORTANTE!)
        'DOWNLOAD_DELAY': 0.5,               # Esperar 0.5s entre peticiones (cortesía)
        'FEED_FORMAT': 'json',               # Guardar resultados en formato JSON
        'FEED_URI': 'farmacias_gps.json',    # Nombre del archivo de salida
    }
    
    # URLs iniciales
    start_urls = [
        "http://www.farmasturias.org/GESCOF/cms/Guardias/FarmaciaBuscar.asp?IdMenu=111"
    ]
    
    def parse(self, response):
        """
        Procesa la página principal de farmacias.
        Extrae datos básicos y genera peticiones para los mapas.
        """
        print(f"\n Procesando página principal: {response.url}")
        
        # Seleccionar todas las farmacias
        farmacias_nodos = response.xpath("//ul[@class='ListadoResultados']") 
        print(f" Se encontraron {len(farmacias_nodos)} farmacias\n")
        
        for i, nodo in enumerate(farmacias_nodos, 1):
            print(f" Procesando farmacia {i} de {len(farmacias_nodos)}...")
            
            # Extraer datos básicos   
            # Nombre
            nombre_elem = nodo.xpath(".//span[@class='TituloResultado']/text()").get()
            nombre = nombre_elem.strip() if nombre_elem else "Sin nombre"
            
            # Dirección
            direccion_elem = nodo.xpath(".//span[@class='ico-localizacion']/text()").get()
            if direccion_elem:
                direccion = direccion_elem.replace("Direccion:&nbsp;", "").replace("Direccion: ", "")
                direccion = direccion.replace("Dirección:&nbsp;", "").replace("Dirección: ", "")
                direccion = direccion.strip()
            else:
                direccion = "Sin dirección"
            
            # Código postal (de la dirección)
            codigo_postal = 0
            if "-" in direccion:
                try:
                    cp_str = direccion.split("-")[-1].strip()
                    codigo_postal = int(cp_str)
                except ValueError:
                    codigo_postal = 0
            
            # Teléfono
            telefono_elem = nodo.xpath(".//span[@class='ico-telefono']/text()").get()
            if telefono_elem:
                telefono = telefono_elem.replace("Teléfono:&nbsp;", "").replace("Teléfono: ", "")
                telefono = telefono.replace("Teléfono:&nbsp;", "").replace("Teléfono: ", "")
                telefono = telefono.strip()
            else:
                telefono = "Sin teléfono"
            
            # Población
            poblacion_elem = nodo.xpath("preceding::h6[@class='LocalidadGuardias']/text()").get()
            poblacion = poblacion_elem.strip() if poblacion_elem else "Sin población"
            
            # Horario
            horario_elem = nodo.xpath("preceding::h5[@class='HorarioGuardias']/a/text()").get()
            horario = horario_elem.strip() if horario_elem else "Sin horario"
            
            # Extraer parámetros del enlace "Ver Mapa" 
            enlace_mapa = nodo.xpath(".//a[@class='VerMapa']/@href").get()
            
            if enlace_mapa:
                params = re.findall(r"'([^']*)'", enlace_mapa) # Extrae los parámetros entre comillas simples
                
                if len(params) >= 5:
                    # Los parámetros que nos interesan: dirección, código postal, número de farmacia
                    direccion_mapa = params[0]      # Dirección completa
                    cp_mapa = params[3]             # Código postal
                    num_farmacia = params[5]        # Número de farmacia
                    
                    # Construir URL del mapa
                    from urllib.parse import quote
                    url_mapa = f"https://www.farmasturias.org/GESCOF/cms/Guardias/openstreetmap.asp?Dir={quote(direccion_mapa)}&Far={num_farmacia}"
                    
                    print(f"     Construyendo URL del mapa para {nombre}")
                    
                    # Crear diccionario con los datos que ya tenemos
                    item = {
                        'nombre': nombre,
                        'direccion': direccion,
                        'codigo_postal': codigo_postal,
                        'telefono': telefono,
                        'poblacion': poblacion,
                        'horario': horario,
                        'latitud': None,
                        'longitud': None
                    }
                    
                    # Hacer una nueva petición a la página del mapa
                    # Cuando termine, llamará a parse_mapa y le pasará el item
                    yield scrapy.Request(
                        url=url_mapa,
                        callback=self.parse_mapa,
                        cb_kwargs={'item': item}
                    )
                else:
                    print(f"     No se pudieron extraer parámetros del enlace")
                    # Si no hay enlace válido, entregamos el item sin coordenadas
                    yield item
            else:
                print(f"     No tiene enlace 'Ver Mapa'")
                yield item
    
    def parse_mapa(self, response, item): # Procesa la página del mapa para extraer latitud y longitud
        # Buscar latitud en el código JavaScript
        # Busca: var latitudfarma='43.12345';
        latitud_match = re.search(r"var latitudfarma='([^']+)'", response.text)
        if latitud_match:
            try:
                latitud = float(latitud_match.group(1))
                item['latitud'] = latitud
            except ValueError:
                item['latitud'] = None
        
        # Buscar longitud
        longitud_match = re.search(r"var longitudfarma='([^']+)'", response.text)
        if longitud_match:
            try:
                longitud = float(longitud_match.group(1))
                item['longitud'] = longitud
            except ValueError:
                item['longitud'] = None
        
        # Validar con Pydantic (opcional)
        try:
            farmacia = Farmacia(**item)
            print(f"    {item['nombre']} - GPS: {item['latitud']}, {item['longitud']}")
            yield farmacia.model_dump()
        except ValidationError as e:
            print(f"    Error al validar: {e}")
            yield item
