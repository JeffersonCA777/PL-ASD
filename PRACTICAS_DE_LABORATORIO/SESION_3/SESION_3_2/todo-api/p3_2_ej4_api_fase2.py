from fastapi import FastAPI, Depends, HTTPException # Importamos FastAPI, Depends para inyección de dependencias y HTTPException para manejar errores
from fastapi.middleware.cors import CORSMiddleware # Middleware para permitir CORS 
from sqlmodel import SQLModel, Field, create_engine, Session, select # Importamos SQLModel para definir modelos, Field para campos de modelo, create_engine para conectar a la base de datos, Session para manejar sesiones y select para consultas
from typing import Optional # Para indicar que un valor puede ser None

class TaskBase(SQLModel): # Modelo base para tareas, sin ID
    description: str # Descripción de la tarea
    completada: bool = False # Por defecto, la tarea no está completada

class Task(TaskBase, table=True): # Modelo para tareas que se guardan en la base de datos (con ID)
    id: Optional[int] = Field(default=None, primary_key=True) # ID autoincremental, clave primaria

class TaskData(TaskBase): # Modelo para los datos que envía el cliente al crear o modificar una tarea (sin ID)
    pass


# CONFIGURACIÓN DE LA BASE DE DATOS

DATABASE_URL = "sqlite:///tareas.db" # URL de conexión a la base de datos SQLite 
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def create_db_and_tables(): # Función para crear la base de datos y las tablas si no existen
    SQLModel.metadata.create_all(engine)

# INSTANCIA DE FASTAPI

app = FastAPI(title="To-Do List API con SQLite", description="API persistente con base de datos") # Creamos la instancia de FastAPI con un título y descripción para la documentación automática


# CONFIGURACIÓN CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
) # Middleware para permitir solicitudes desde cualquier origen, con cualquier método y encabezados


# DEPENDENCIAS

def get_db(): # Función para obtener una sesión de base de datos, que se cerrará automáticamente al finalizar la solicitud
    with Session(engine) as db:
        yield db

class TaskRepository: # Repositorio de tareas que interactúa con la base de datos
    
    def __init__(self, db: Session): # Inicializa el repositorio con una sesión de base de datos
        self.db = db
    
    def get_all(self) -> list[Task]: # Devuelve la lista completa de tareas desde la base de datos
        return self.db.exec(select(Task)).all()
    
    def get_by_id(self, id: int) -> Optional[Task]: # Busca una tarea por su ID en la base de datos
        return self.db.get(Task, id)
    
    def add(self, task_data: TaskData) -> Task: # Crea una nueva tarea en la base de datos con los datos recibidos
        task = Task(description=task_data.description, completada=task_data.completada)
        self.db.add(task) # Agrega la nueva tarea a la sesión de base de datos
        self.db.commit()
        self.db.refresh(task) # Refresca la tarea para obtener el ID generado por la base de datos
        return task
    
    def update(self, id: int, task_data: TaskData) -> Optional[Task]: # Actualiza una tarea existente en la base de datos con los nuevos datos
        task = self.db.get(Task, id) # Busca la tarea por ID en la base de datos
        if not task:
            return None
        task.description = task_data.description
        task.completada = task_data.completada
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def delete(self, id: int) -> bool: # Elimina una tarea de la base de datos por su ID
        task = self.db.get(Task, id)
        if not task:
            return False
        self.db.delete(task) # Elimina la tarea de la sesión de base de datos
        self.db.commit()
        return True

def get_repo(db: Session = Depends(get_db)) -> TaskRepository: # Función de dependencia para obtener una instancia del repositorio de tareas con la sesión de base de datos
    return TaskRepository(db)


# ENDPOINTS (IDÉNTICOS AL EJERCICIO 2)

@app.get("/tasks", response_model=list[Task]) # Endpoint para obtener la lista de todas las tareas, devuelve una lista de objetos Task
def list_tasks(repo: TaskRepository = Depends(get_repo)) -> list[Task]:
    return repo.get_all()

@app.post("/tasks", response_model=Task, status_code=201) # Endpoint para crear una nueva tarea, recibe un objeto TaskData y devuelve el objeto Task creado con ID
def create_task(task_in: TaskData, repo: TaskRepository = Depends(get_repo)) -> Task:
    return repo.add(task_in)

@app.get("/tasks/{id}", response_model=Task) # Endpoint para obtener una tarea por su ID, devuelve un objeto Task o un error 404 si no se encuentra
def get_task(id: int, repo: TaskRepository = Depends(get_repo)) -> Task:
    task = repo.get_by_id(id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task

@app.put("/tasks/{id}", response_model=Task) # Endpoint para actualizar una tarea por su ID, recibe un objeto TaskData con los nuevos datos y devuelve el objeto Task actualizado o un error 404 si no se encuentra
def update_task(id: int, task_in: TaskData, repo: TaskRepository = Depends(get_repo)) -> Task:
    task = repo.update(id, task_in)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task

@app.delete("/tasks/{id}", status_code=204) # Endpoint para eliminar una tarea por su ID, devuelve un código de estado 204 si se elimina correctamente o un error 404 si no se encuentra
def delete_task(id: int, repo: TaskRepository = Depends(get_repo)):
    if not repo.delete(id):
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return


# CREAR TABLAS AL INICIAR

create_db_and_tables()