from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# ============================================
# ESQUEMAS PYDANTIC
# ============================================

class TaskData(BaseModel):
    """Datos que envía el cliente para crear/modificar una tarea (sin ID)"""
    description: str
    completada: bool = False

class Task(TaskData):
    """Datos que devuelve el servidor (con ID)"""
    id: int


# ============================================
# REPOSITORIO EN MEMORIA
# ============================================

class TaskRepository:
    """Almacena las tareas en una lista en memoria"""
    
    def __init__(self):
        """Inicializa la lista vacía y el contador de IDs"""
        self.tasks = []
        self.next_id = 1
    
    def _find_task_index(self, id: int) -> Optional[int]:
        """Busca el índice de una tarea por su ID. Devuelve el índice o None"""
        for i, task in enumerate(self.tasks):
            if task.id == id:
                return i
        return None
    
    def get_all(self) -> list[Task]:
        """Devuelve la lista completa de tareas"""
        return self.tasks
    
    def get_by_id(self, id: int) -> Optional[Task]:
        """Busca una tarea por su ID. Devuelve Task o None"""
        index = self._find_task_index(id)
        if index is not None:
            return self.tasks[index]
        return None
    
    def add(self, task_data: TaskData) -> Task:
        """Crea una nueva tarea y la añade a la lista"""
        new_task = Task(
            id=self.next_id,
            description=task_data.description,
            completada=task_data.completada
        )
        self.tasks.append(new_task)
        self.next_id += 1
        return new_task
    
    def update(self, id: int, task_data: TaskData) -> Optional[Task]:
        """Actualiza una tarea existente. Devuelve la tarea actualizada o None"""
        index = self._find_task_index(id)
        if index is None:
            return None
        
        task = self.tasks[index]
        task.description = task_data.description
        task.completada = task_data.completada
        return task
    
    def delete(self, id: int) -> bool:
        """Elimina una tarea. Devuelve True si se borró, False si no existía"""
        index = self._find_task_index(id)
        if index is None:
            return False
        
        self.tasks.pop(index)
        return True


# ============================================
# INSTANCIA DE FASTAPI
# ============================================

app = FastAPI(title="To-Do List API", description="API para gestionar una lista de tareas")


# ============================================
# CONFIGURACIÓN CORS (para poder probar desde el navegador)
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # En desarrollo permitimos cualquier origen
    allow_methods=["*"],        # Permitimos todos los verbos HTTP
    allow_headers=["*"],        # Permitimos todas las cabeceras
)


# ============================================
# DEPENDENCIA: función que devuelve el repositorio
# ============================================

# IMPORTANTE: Creamos UNA SOLA instancia global del repositorio
# Así todos los endpoints comparten la misma lista de tareas
_repo = TaskRepository()

def get_repo() -> TaskRepository:
    """Devuelve la instancia global del repositorio en memoria"""
    return _repo


# ============================================
# ENDPOINTS DE LA API
# ============================================

@app.get("/tasks", response_model=list[Task])
def list_tasks(repo: TaskRepository = Depends(get_repo)) -> list[Task]:
    """
    Obtiene la lista de todas las tareas.
    """
    return repo.get_all()


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task_in: TaskData, repo: TaskRepository = Depends(get_repo)) -> Task:
    """
    Crea una nueva tarea. El servidor asigna automáticamente un ID único.
    """
    return repo.add(task_in)


@app.get("/tasks/{id}", response_model=Task)
def get_task(id: int, repo: TaskRepository = Depends(get_repo)) -> Task:
    """
    Obtiene una tarea específica por su ID.
    Si no existe, devuelve error 404.
    """
    task = repo.get_by_id(id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task


@app.put("/tasks/{id}", response_model=Task)
def update_task(id: int, task_in: TaskData, repo: TaskRepository = Depends(get_repo)) -> Task:
    """
    Actualiza completamente una tarea existente.
    Si no existe, devuelve error 404.
    """
    task = repo.update(id, task_in)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task


@app.delete("/tasks/{id}", status_code=204)
def delete_task(id: int, repo: TaskRepository = Depends(get_repo)):
    """
    Elimina una tarea existente.
    Si no existe, devuelve error 404.
    Si se elimina correctamente, devuelve código 204 sin contenido.
    """
    if not repo.delete(id):
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return  # No devuelve contenido, solo el código 204