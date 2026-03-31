from p3_2_ej1_api_fase1 import TaskData, TaskRepository

print("=== PROBANDO EL REPOSITORIO ===\n")

# Crear una instancia del repositorio
repo = TaskRepository()

# 1. Crear algunas tareas
print("1. Creando tareas...")
t1 = repo.add(TaskData(description="Comprar pan", completada=False))
t2 = repo.add(TaskData(description="Estudiar para el examen", completada=False))
t3 = repo.add(TaskData(description="Pasear al perro", completada=True))
print(f"   Tarea creada: ID={t1.id}, {t1.description}")
print(f"   Tarea creada: ID={t2.id}, {t2.description}")
print(f"   Tarea creada: ID={t3.id}, {t3.description}")

# 2. Obtener todas las tareas
print("\n2. Todas las tareas:")
for t in repo.get_all():
    print(f"   ID: {t.id}, Desc: {t.description}, Completada: {t.completada}")

# 3. Obtener una tarea por ID
print(f"\n3. Buscar tarea ID=1: {repo.get_by_id(1).description}")

# 4. Buscar una tarea que no existe
print(f"\n4. Buscar tarea ID=999: {repo.get_by_id(999)} (debe ser None)")

# 5. Actualizar una tarea
print("\n5. Actualizando tarea ID=1...")
repo.update(1, TaskData(description="Comprar pan y leche", completada=True))
tarea_actualizada = repo.get_by_id(1)
print(f"   Tarea actualizada: {tarea_actualizada.description}, completada={tarea_actualizada.completada}")

# 6. Eliminar una tarea
print(f"\n6. Eliminando tarea ID=2...")
resultado = repo.delete(2)
print(f"   ¿Se borró? {resultado}")

# 7. Ver lista final
print("\n7. Lista final de tareas:")
for t in repo.get_all():
    print(f"   ID: {t.id}, Desc: {t.description}, Completada: {t.completada}")

print("\n=== PRUEBA COMPLETADA ===")