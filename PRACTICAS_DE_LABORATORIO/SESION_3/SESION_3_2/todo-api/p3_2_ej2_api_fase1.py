"""
Ejercicio 2: API REST completa con FastAPI y repositorio en memoria

En este segundo ejercicio se implementa una API REST completa para gestionar
una lista de tareas. Se incluyen los endpoints GET, POST, PUT y DELETE,
configuración CORS, inyección de dependencias y manejo de errores con HTTPException.
"""

# 1: IMPORTACIÓN DE LIBRERÍAS
from fastapi import FastAPI, Depends, HTTPException # Importamos FastAPI, Depends para de dependencias y HTTPException para manejar errores
from fastapi.middleware.cors import CORSMiddleware # Middleware para configurar CORS 
from pydantic import BaseModel # Importamos BaseModel de Pydantic para definir los esquemas de datos
from typing import Optional # Importamos Optional para indicar que un valor puede ser None

# 2: ESQUEMAS PYDANTIC

class TaskData(BaseModel): # Esquema para la creación y actualización de tareas
    description: str
    completada: bool = False

class Task(TaskData): # Esquema que extiende TaskData e incluye el campo id
    id: int

# 3: REPOSITORIO EN MEMORIA

class TaskRepository: # Clase que actúa como repositorio en memoria para gestionar las tareas
    
    def __init__(self): # Inicializamos la lista de tareas y el siguiente ID disponible
        self.tasks = []
        self.next_id = 1
    
    def _find_task_index(self, id: int) -> Optional[int]: # Método privado para encontrar el índice de una tarea por su ID
        for i, task in enumerate(self.tasks):
            if task.id == id:
                return i
        return None
    
    def get_all(self) -> list[Task]: # Método para obtener todas las tareas
        return self.tasks
    
    def get_by_id(self, id: int) -> Optional[Task]: # Método para obtener una tarea por su ID
        index = self._find_task_index(id)
        if index is not None:
            return self.tasks[index]
        return None
    
    def add(self, task_data: TaskData) -> Task: # Método para agregar una nueva tarea al repositorio
        new_task = Task(
            id=self.next_id,
            description=task_data.description,
            completada=task_data.completada
        )
        self.tasks.append(new_task)
        self.next_id += 1
        return new_task
    
    def update(self, id: int, task_data: TaskData) -> Optional[Task]: # Método para actualizar una tarea existente
        index = self._find_task_index(id)
        if index is None:
            return None
        
        task = self.tasks[index]
        task.description = task_data.description
        task.completada = task_data.completada
        return task
    
    def delete(self, id: int) -> bool: # Método para eliminar una tarea por su ID
        index = self._find_task_index(id)
        if index is None:
            return False
        
        self.tasks.pop(index)
        return True

# 4: INSTANCIA DE FASTAPI

app = FastAPI(title="To-Do List API", description="API para gestionar una lista de tareas") # Creamos una instancia de FastAPI con un título y descripción para la documentación automática

# 5: CONFIGURACIÓN CORS (para poder probar desde el navegador)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # En desarrollo permitimos cualquier origen
    allow_methods=["*"],        # Permitimos todos los verbos HTTP
    allow_headers=["*"],        # Permitimos todas las cabeceras
)

# 6: DEPENDENCIA: función que devuelve el repositorio

_repo = TaskRepository()

def get_repo() -> TaskRepository: # Función de dependencia que devuelve la instancia del repositorio
    return _repo

# 7: ENDPOINTS DE LA API

@app.get("/tasks", response_model=list[Task]) # Endpoint para obtener todas las tareas, devuelve una lista de objetos Task
def list_tasks(repo: TaskRepository = Depends(get_repo)) -> list[Task]:
    return repo.get_all()


@app.post("/tasks", response_model=Task, status_code=201) # Endpoint para crear una nueva tarea, recibe un objeto TaskData y devuelve el objeto Task creado con su ID asignado
def create_task(task_in: TaskData, repo: TaskRepository = Depends(get_repo)) -> Task:
    return repo.add(task_in)


@app.get("/tasks/{id}", response_model=Task) # Endpoint para obtener una tarea por su ID, devuelve un objeto Task o un error 404 si no se encuentra
def get_task(id: int, repo: TaskRepository = Depends(get_repo)) -> Task:
    task = repo.get_by_id(id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task


@app.put("/tasks/{id}", response_model=Task) # Endpoint para actualizar una tarea existente, recibe un objeto TaskData y devuelve el objeto Task actualizado o un error 404 si no se encuentra
def update_task(id: int, task_in: TaskData, repo: TaskRepository = Depends(get_repo)) -> Task:
    task = repo.update(id, task_in)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task


@app.delete("/tasks/{id}", status_code=204) # Endpoint para eliminar una tarea por su ID, devuelve un código 204 No Content si se elimina correctamente o un error 404 si no se encuentra
def delete_task(id: int, repo: TaskRepository = Depends(get_repo)):
    if not repo.delete(id):
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return  # No devuelve contenido, solo el código 204

# 8: PUNTO DE ENTRADA DEL PROGRAMA

if __name__ == "__main__":
    pass