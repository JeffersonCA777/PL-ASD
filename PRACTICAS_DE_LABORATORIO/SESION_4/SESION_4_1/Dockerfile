FROM python:3.11

RUN pip install uv
RUN uv pip install --system fastapi uvicorn

RUN mkdir /miapp
COPY ./hola.py /miapp

WORKDIR /miapp

CMD ["uvicorn", "hola:app", "--host", "0.0.0.0", "--port", "5000"]
