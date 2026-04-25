"""
Ejercicio 1: API REST para gestión de tareas.
En este primer ejercicio se implementa la capa de datos de la API de lista de tareas.
Se definen los esquemas Pydantic para la validación de datos
y la clase TaskRepository.
"""

# 1. Importar las librerías necesarias
from pydantic import BaseModel # Para definir los esquemas de datos
from typing import Optional # Para indicar que un valor puede ser None

# 2. Esquemas Pydantic para la validación de datos
class TaskData(BaseModel):
    """Datos que envía el cliente para crear/modificar una tarea"""
    description: str # Descripción de la tarea
    completada: bool = False # Por defecto, la tarea no está completada

class Task(TaskData):
    """Datos que devuelve el servidor (con ID)"""
    id: int # Identificador único de la tarea

# 3. Repositorio en memoria para almacenar las tareas
class TaskRepository:
    """Almacena las tareas en una lista en memoria"""
    
    def __init__(self):
        """Inicializa la lista vacía y el contador de IDs"""
        self.tasks = []      # Lista donde se guardan las tareas
        self.next_id = 1     # Próximo ID a asignar
    
    def _find_task_index(self, id: int) -> Optional[int]:
        for i, task in enumerate(self.tasks): # Buscar la tarea por ID y devolver su índice
            if task.id == id: # Si encontramos la tarea con el ID buscado, devolvemos su índice
                return i
        return None
    
    def get_all(self) -> list[Task]:
        return self.tasks # Devuelve la lista completa de tareas
    
    def get_by_id(self, id: int) -> Optional[Task]:
        index = self._find_task_index(id) # Buscar la tarea por ID y devolverla si existe
        if index is not None:
            return self.tasks[index] # Si encontramos la tarea, la devolvemos
        return None
    
    def add(self, task_data: TaskData) -> Task:
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
        index = self._find_task_index(id) # Buscar la tarea por ID y actualizarla si existe
        if index is None:
            return None # Si no encontramos la tarea con el ID dado, devolvemos None
        
        # Actualizar los campos de la tarea existente
        task = self.tasks[index] # Obtener la tarea que queremos actualizar
        task.description = task_data.description # Actualizar la descripción con el nuevo valor
        task.completada = task_data.completada # Actualizar el estado de completada con el nuevo valor
        
        return task
    
    def delete(self, id: int) -> bool:
        index = self._find_task_index(id) # Buscar la tarea por ID y eliminarla si existe
        if index is None:
            return False # Si no encontramos la tarea con el ID dado, devolvemos False
        
        # Eliminar la tarea de la lista
        self.tasks.pop(index)
        return True
    
# 4. Punto de entrada del programa
if __name__ == "__main__":
    pass