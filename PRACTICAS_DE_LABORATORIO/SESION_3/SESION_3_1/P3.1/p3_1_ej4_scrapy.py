import scrapy # Librería principal de Scrapy para crear spiders
from pydantic import BaseModel, ValidationError # Pydantic para definir modelos de datos y validación

# PARTE 1: Definir el modelo de datos 
class Farmacia(BaseModel): # Modelo de datos para representar una farmacia
    nombre: str # Nombre de la farmacia
    direccion: str # Dirección de la farmacia
    codigo_postal: int # Código postal 
    telefono: str # Teléfono de la farmacia
    poblacion: str # Población donde se encuentra la farmacia
    horario: str # Horario de guardia 

# PARTE 2: Definir el Spider
class FarmaciaSpider(scrapy.Spider): # Clase que define el spider para extraer datos de farmacias
    # Nombre único del spider (para identificarlo al ejecutar)
    name = "farmacias"
    
    # Configuración personalizada
    custom_settings = {
        'HTTPCACHE_ENABLED': True,      # Activar caché HTTP
        'FEED_FORMAT': 'json',           # Formato de salida
        'FEED_URI': 'farmacias_scrapy.json',  # Archivo de salida
    }
    
    # URLs iniciales donde empezará el scraping
    start_urls = [
        "http://www.farmasturias.org/GESCOF/cms/Guardias/FarmaciaBuscar.asp?IdMenu=111"
    ]
    
    def parse(self, response): # Método principal que procesa la respuesta de cada página
        print(f"\n Procesando página: {response.url}")
        print(f" Tamaño de respuesta: {len(response.text)} bytes\n")
        
        # 1. Seleccionar todas las farmacias 
        # Cada farmacia está dentro de un <ul class="ListadoResultados">
        farmacias_nodos = response.xpath("//ul[@class='ListadoResultados']")
        print(f" Se encontraron {len(farmacias_nodos)} farmacias\n")
        
        # 2. Procesar cada farmacia 
        for i, nodo in enumerate(farmacias_nodos, 1):
            print(f" Procesando farmacia {i} de {len(farmacias_nodos)}...")
            
            # 2.1 Extraer nombre
            nombre_elem = nodo.xpath(".//span[@class='TituloResultado']/text()").get()
            nombre = nombre_elem.strip() if nombre_elem else "Sin nombre"
            
            # 2.2 Extraer dirección 
            direccion_elem = nodo.xpath(".//span[@class='ico-localizacion']/text()").get()
            if direccion_elem:
                # Limpiar: quitar "Direccion:&nbsp;" y "Direccion: "
                direccion = direccion_elem.replace("Direccion:&nbsp;", "").replace("Direccion: ", "")
                direccion = direccion.replace("Dirección:&nbsp;", "").replace("Dirección: ", "")
                direccion = direccion.strip()
            else:
                direccion = "Sin dirección"
            
            # 2.3 Extraer código postal
            codigo_postal = 0
            if "-" in direccion:
                try:
                    cp_str = direccion.split("-")[-1].strip()
                    codigo_postal = int(cp_str)
                except ValueError:
                    codigo_postal = 0
            
            # 2.4 Extraer teléfono
            telefono_elem = nodo.xpath(".//span[@class='ico-telefono']/text()").get()
            if telefono_elem:
                telefono = telefono_elem.replace("Teléfono:&nbsp;", "").replace("Teléfono: ", "")
                telefono = telefono.replace("Teléfono:&nbsp;", "").replace("Teléfono: ", "")
                telefono = telefono.strip()
            else:
                telefono = "Sin teléfono"
            
            # 2.5 Extraer población 
            poblacion_elem = nodo.xpath("preceding::h6[@class='LocalidadGuardias']/text()").get()
            if poblacion_elem:
                poblacion = poblacion_elem.strip()
            else:
                poblacion = "Sin población"
            
            # 2.6 Extraer horario 
            horario_elem = nodo.xpath("preceding::h5[@class='HorarioGuardias']/a/text()").get()
            if horario_elem:
                horario = horario_elem.strip()
            else:
                horario = "Sin horario"
            
            # 2.7 Validar con Pydantic 
            try:
                farmacia = Farmacia( # Crear instancia del modelo con los datos extraídos
                    nombre=nombre,
                    direccion=direccion,
                    codigo_postal=codigo_postal,
                    telefono=telefono,
                    poblacion=poblacion,
                    horario=horario
                )
                print(f"    {nombre} - {poblacion}")
                
                # Devolver los datos como diccionario (Scrapy lo guardará automáticamente)
                yield farmacia.model_dump()
                
            except ValidationError as e:
                print(f"    Error al validar: {e}")
                continue
        
        print("\n Spider completado!")