from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/saluda", response_class=HTMLResponse)
def saludar(nombre: str = "anonimo"):
    documento = '<html><head><title>Saludar</title></head>'
    documento += '<body><div id="saludo">Hola {}</div></body>'
    documento += '</html>\n'
    return documento.format(nombre)
