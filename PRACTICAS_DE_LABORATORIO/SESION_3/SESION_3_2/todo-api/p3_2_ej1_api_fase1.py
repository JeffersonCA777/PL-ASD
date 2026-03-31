from pydantic import BaseModel # Para definir los esquemas de datos
from typing import Optional # Para indicar que un valor puede ser None

# Esquemas de datos para las tareas
class TaskData(BaseModel):
    """Datos que envía el cliente para crear/modificar una tarea (sin ID)"""
    description: str
    completada: bool = False

class Task(TaskData):
    """Datos que devuelve el servidor (con ID)"""
    id: int

# Repositorio de tareas
class TaskRepository:
    """Almacena las tareas en una lista en memoria"""
    
    def __init__(self):
        """Inicializa la lista vacía y el contador de IDs"""
        self.tasks = []      # Lista donde se guardan las tareas
        self.next_id = 1     # Próximo ID a asignar
    
    def _find_task_index(self, id: int) -> Optional[int]:
        """
        Método auxiliar "privado" (por eso empieza con _)
        Busca el índice de una tarea por su ID.
        Devuelve el índice si la encuentra, o None si no.
        """
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
        # Crear la tarea con ID y los datos recibidos
        new_task = Task(
            id=self.next_id,
            description=task_data.description,
            completada=task_data.completada
        )
        # Añadir a la lista
        self.tasks.append(new_task)
        # Incrementar el contador para el próximo ID
        self.next_id += 1
        # Devolver la tarea creada
        return new_task
    
    def update(self, id: int, task_data: TaskData) -> Optional[Task]:
        """Actualiza una tarea existente. Devuelve la tarea actualizada o None"""
        index = self._find_task_index(id)
        if index is None:
            return None
        
        # Actualizar los campos de la tarea existente
        task = self.tasks[index]
        task.description = task_data.description
        task.completada = task_data.completada
        
        return task
    
    def delete(self, id: int) -> bool:
        """Elimina una tarea. Devuelve True si se borró, False si no existía"""
        index = self._find_task_index(id)
        if index is None:
            return False
        
        # Eliminar la tarea de la lista
        self.tasks.pop(index)
        return True