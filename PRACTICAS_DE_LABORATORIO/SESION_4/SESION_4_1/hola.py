"""
Aplicacion FastAPI para el de despliegue de servicios en contenedores.
Esta aplicacion expone un endpoint /saluda que devuelve una pagina HTML
con un saludo personalizado. 
"""

# 1. Librerias
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# 2. Inicializacion de la aplicacion
app = FastAPI()

# 3. Definicion de endpoints
@app.get("/saluda", response_class=HTMLResponse)
def saludar(nombre: str = "anonimo"): # El parametro nombre es opcional, si no se proporciona se usara "anonimo"
    documento = '<html><head><title>Saludar</title></head>'
    documento += '<body><div id="saludo">Hola {}</div></body>'
    documento += '</html>\n'
    return documento.format(nombre)

# 4. Punto de entrada del programa
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
