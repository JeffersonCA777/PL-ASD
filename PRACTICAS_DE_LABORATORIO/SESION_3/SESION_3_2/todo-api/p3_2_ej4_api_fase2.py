from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional

# ============================================
# MODELO UNIFICADO (Base de Datos + Esquema API)
# ============================================

class TaskBase(SQLModel):
    """Campos comunes entre TaskData y Task"""
    description: str
    completada: bool = False

class Task(TaskBase, table=True):
    """Modelo para la Base de Datos (SQL) y para respuestas GET"""
    id: Optional[int] = Field(default=None, primary_key=True)

class TaskData(TaskBase):
    """Modelo para recibir datos en POST y PUT (sin ID)"""
    pass


# ============================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# ============================================

DATABASE_URL = "sqlite:///tareas.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """Crea las tablas en la base de datos si no existen"""
    SQLModel.metadata.create_all(engine)


# ============================================
# INSTANCIA DE FASTAPI
# ============================================

app = FastAPI(title="To-Do List API con SQLite", description="API persistente con base de datos")


# ============================================
# CONFIGURACIÓN CORS
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# DEPENDENCIAS
# ============================================

def get_db():
    """Devuelve una sesión de base de datos y la cierra al terminar"""
    with Session(engine) as db:
        yield db

class TaskRepository:
    """Repositorio que usa base de datos SQLite"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> list[Task]:
        """Devuelve todas las tareas"""
        return self.db.exec(select(Task)).all()
    
    def get_by_id(self, id: int) -> Optional[Task]:
        """Devuelve una tarea por ID o None"""
        return self.db.get(Task, id)
    
    def add(self, task_data: TaskData) -> Task:
        """Crea una nueva tarea"""
        task = Task(description=task_data.description, completada=task_data.completada)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def update(self, id: int, task_data: TaskData) -> Optional[Task]:
        """Actualiza una tarea existente"""
        task = self.db.get(Task, id)
        if not task:
            return None
        task.description = task_data.description
        task.completada = task_data.completada
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def delete(self, id: int) -> bool:
        """Elimina una tarea"""
        task = self.db.get(Task, id)
        if not task:
            return False
        self.db.delete(task)
        self.db.commit()
        return True

def get_repo(db: Session = Depends(get_db)) -> TaskRepository:
    """Inyecta el repositorio con la sesión de BD"""
    return TaskRepository(db)


# ============================================
# ENDPOINTS (IDÉNTICOS AL EJERCICIO 2)
# ============================================

@app.get("/tasks", response_model=list[Task])
def list_tasks(repo: TaskRepository = Depends(get_repo)) -> list[Task]:
    return repo.get_all()

@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task_in: TaskData, repo: TaskRepository = Depends(get_repo)) -> Task:
    return repo.add(task_in)

@app.get("/tasks/{id}", response_model=Task)
def get_task(id: int, repo: TaskRepository = Depends(get_repo)) -> Task:
    task = repo.get_by_id(id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task

@app.put("/tasks/{id}", response_model=Task)
def update_task(id: int, task_in: TaskData, repo: TaskRepository = Depends(get_repo)) -> Task:
    task = repo.update(id, task_in)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task

@app.delete("/tasks/{id}", status_code=204)
def delete_task(id: int, repo: TaskRepository = Depends(get_repo)):
    if not repo.delete(id):
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return


# ============================================
# CREAR TABLAS AL INICIAR
# ============================================

create_db_and_tables()