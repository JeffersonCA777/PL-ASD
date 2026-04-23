"""
Ejercicio 1 (Opcional): Autenticación y seguridad.
En este primer ejercicio opcional, se implementará la autenticación y seguridad en la API de tareas. 
Para ello se usarán JWT (Jason Web Tokens). Por cual incluye registro de usuarios, login y protección de rutas.
"""

import os # Se importa os para manejar variables de entorno
from fastapi import FastAPI, Depends, HTTPException, status # Se importan las clases y funciones necesarias de FastAPI para crear la aplicación, manejar dependencias, excepciones HTTP y códigos de estado.
from fastapi.middleware.cors import CORSMiddleware # Se importa CORSMiddleware para manejar el CORS en la aplicación.
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm # Se importan las bibliotecas necesarias para manejar la autenticación con OAuth2 y JWT.
from sqlmodel import SQLModel, Field, Relationship, create_engine, Session, select # Se importan las clases y funciones necesarias de SQLModel.
from datetime import datetime, timedelta, timezone # Se importan las clases necesarias para manejar fechas y tiempos.
from jose import JWTError, jwt # Se importan las clases necesarias para manejar JWT.
import bcrypt # Se importa bcrypt para manejar el hashing de contraseñas.
from typing import Optional, List # Se importan las clases necesarias para manejar tipos de datos opcionales y listas.

# Configuración de la aplicación FastAPI
app = FastAPI(title="To-Do API con Autenticacion")

# Configuración de CORS para permitir solicitudes desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite solicitudes desde cualquier origen.
    allow_credentials=True, # Permite el envío de cookies y credenciales en las solicitudes.
    allow_methods=["*"], # Permite todos los métodos HTTP.
    allow_headers=["*"], # Permite todos los encabezados HTTP.
)

# Configuración de JWT
SECRET_KEY = "mi_clave_secreta_super_segura_para_desarrollo"
ALGORITHM = "HS256"

# Configuración de OAuth2 para manejar la autenticación con JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Definición de los modelos de datos usando SQLModel
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True) # Campo de ID.
    username: str = Field(unique=True, index=True) # Campo de nombre de usuario.
    hashed_password: str # Campo de contraseña hasheada.
    tasks: List["Task"] = Relationship(back_populates="owner") 

# Esquema base para crear y actualizar tareas, sin incluir campos de base de datos.
class TaskBase(SQLModel):
    description: str # Campo de descripción de la tarea.
    completed: bool = False 

# Esquema de tarea en la base de datos para asociar con un usuario.
class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True) # Campo de ID.
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id") # Campo de ID del propietario.
    owner: Optional[User] = Relationship(back_populates="tasks") 

# Esquema para recibir datos de usuario en el registro y login.
class UserData(SQLModel):
    username: str 
    password: str

# Esquema para la respuesta del token/endpoint con el JWT.
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer" 

# Configuración de la base de datos usando SQLite y SQLModel.
DATABASE_URL = "sqlite:///./tareas.db"
engine = create_engine(DATABASE_URL, echo=True)

# Funciones para manejar la base de datos, autenticación y autorización.
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Función para obtener una sesión de base de datos.
def get_db():
    with Session(engine) as session:
        yield session

# Función para generar hash de la contraseña usando bcrypt.
def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

# Función para verificar la contraseña coincide con el hash almacenado.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

# Función para crear un token JWT con los datos del usuario y una fecha de expiración.  
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta: 
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire}) # Se agrega la fecha de expiración al payload del token.
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Función para obtener el usuario autenticado a partir del token JWT. 
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException( # Excepción para manejar errores de autenticación.
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # Se decodifica el token JWT para obtener el payload.
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError: # Si ocurre un error al decodificar el token.
        raise credentials_exception
    user = db.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user

# Repositorio para manejar, acceder y modificar  tareas.
class TaskRepository:
    def __init__(self, db: Session, user_id: int): # Se inicializa con una sesión de base de datos y el ID del usuario autenticado.
        self.db = db
        self.user_id = user_id
    
    def get_all(self) -> List[Task]: # Se retorna todas las tareas del usuario autenticado.
        statement = select(Task).where(Task.owner_id == self.user_id)
        return list(self.db.exec(statement).all())
    
    def get_by_id(self, task_id: int) -> Optional[Task]: # Se retorna una tarea si pertenece al usuario autenticado.
        statement = select(Task).where(
            Task.id == task_id,
            Task.owner_id == self.user_id
        )
        return self.db.exec(statement).first()
    
    def create(self, task_data: TaskBase) -> Task: # Se crea una nueva tarea para usuario autenticado.
        db_task = Task(
            description=task_data.description,
            completed=task_data.completed,
            owner_id=self.user_id
        )
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task
    
    def update(self, task_id: int, task_data: TaskBase) -> Optional[Task]: # Se actualiza una tarea si pertenece al usuario autenticado.
        db_task = self.get_by_id(task_id)
        if db_task is None:
            return None
        db_task.description = task_data.description
        db_task.completed = task_data.completed # Se actualizan los campos de la tarea.
        self.db.commit()
        self.db.refresh(db_task)
        return db_task
    
    def delete(self, task_id: int) -> bool: # Se elimina una tarea si pertenece al usuario autenticado.
        db_task = self.get_by_id(task_id)
        if db_task is None:
            return False
        self.db.delete(db_task) # Se elimina la tarea de la base de datos.
        self.db.commit()
        return True

# Función para obtener una dependecia de TaskRepository para el usuario autenticado.
def get_repo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Se obtiene el usuario autenticado para crear un repositorio.
) -> TaskRepository:
    return TaskRepository(db, current_user.id)

@app.post("/users", status_code=status.HTTP_201_CREATED)
def register_user( # Endpoint para registrar un nuevo usuario.
    user_in: UserData,
    db: Session = Depends(get_db)
):
    hashed_pwd = get_password_hash(user_in.password) # Registra un nuevo usuario con el nombre de usuario y la contraseña hasheada.
    db_user = User(username=user_in.username, hashed_password=hashed_pwd)
    try:
        db.add(db_user) # Se agrega el nuevo usuario.
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    return {"msg": "User created"}

@app.post("/token", response_model=Token)
def login_for_access_token( # Endpoint para auntenticar un usuario y obtener un token JWT.
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token( # Se crea un token JWT con el nombre de usuario.
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@app.get("/tasks", response_model=List[Task])
def list_tasks(repo: TaskRepository = Depends(get_repo)): # Endpoint que retorna todas las tareas del usuario autenticado.
    return repo.get_all()

@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task( # Endpoint para crear una nueva tarea para el usuario autenticado.
    task_data: TaskBase,
    repo: TaskRepository = Depends(get_repo)
):
    return repo.create(task_data)

@app.get("/tasks/{task_id}", response_model=Task)
def get_task( # Endpoint para obtener una tarea específica por ID, solo si pertenece al usuario autenticado.
    task_id: int,
    repo: TaskRepository = Depends(get_repo)
):
    task = repo.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=Task)
def update_task( # Endpoint para actualizar una tarea específica por ID, solo si pertenece al usuario autenticado.
    task_id: int,
    task_data: TaskBase,
    repo: TaskRepository = Depends(get_repo)
):
    task = repo.update(task_id, task_data)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task( # Endpoint para eliminar una tarea específica por ID, solo si pertenece al usuario autenticado.
    task_id: int,
    repo: TaskRepository = Depends(get_repo)
):
    if not repo.delete(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return None

@app.on_event("startup") # Evento que se ejecuta al iniciar la aplicación para crear la base de datos y las tablas.
def on_startup():
    create_db_and_tables()

# Punto de entrada para ejecutar la aplicación con Uvicorn.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) # Se ejecuta la aplicación en el host y puerto