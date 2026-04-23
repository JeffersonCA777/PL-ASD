"""
Ejercicio 2 (Opcional): WebSockets para chat en tiempo real.

En este segundo ejecicio opcional, se extiende la API del ejercicio 1 añadiendo un chat grupal mediante WebSockets.
Los usuarios autenticados pueden enviar mensajes que todos ven al instante.
"""

import os
from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Field, Relationship, create_engine, Session, select
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import bcrypt
from typing import Optional, List

app = FastAPI(title="To-Do API con Autenticacion y Chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "mi_clave_secreta_super_segura_para_desarrollo"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

class User(SQLModel, table=True):
    """Modelo de usuario en la base de datos."""
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    tasks: List["Task"] = Relationship(back_populates="owner")


class TaskBase(SQLModel):
    """Esquema base para crear o actualizar tareas."""
    description: str
    completed: bool = False


class Task(TaskBase, table=True):
    """Modelo de tarea en la base de datos, asociada a un usuario."""
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    owner: Optional[User] = Relationship(back_populates="tasks")


class UserData(SQLModel):
    """Esquema para recibir datos de registro de usuario."""
    username: str
    password: str


class Token(SQLModel):
    """Respuesta del endpoint /token con el JWT."""
    access_token: str
    token_type: str = "bearer"


DATABASE_URL = "sqlite:///./tareas.db"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """Crea las tablas en la base de datos si no existen."""
    SQLModel.metadata.create_all(engine)


def get_db():
    """Dependencia que proporciona una sesion de base de datos."""
    with Session(engine) as session:
        yield session


def get_password_hash(password: str) -> str:
    """Genera un hash seguro de la contraseña usando bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con su hash almacenado."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT con fecha de caducidad."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Obtiene el usuario autenticado a partir del token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user


class TaskRepository:
    """Repositorio para operaciones CRUD de tareas filtradas por usuario."""
    
    def __init__(self, db: Session, user_id: int):
        """Inicializa el repositorio con una sesion y el ID del usuario."""
        self.db = db
        self.user_id = user_id
    
    def get_all(self) -> List[Task]:
        """Retorna todas las tareas del usuario autenticado."""
        statement = select(Task).where(Task.owner_id == self.user_id)
        return list(self.db.exec(statement).all())
    
    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Retorna una tarea si pertenece al usuario autenticado."""
        statement = select(Task).where(
            Task.id == task_id,
            Task.owner_id == self.user_id
        )
        return self.db.exec(statement).first()
    
    def create(self, task_data: TaskBase) -> Task:
        """Crea una nueva tarea para el usuario autenticado."""
        db_task = Task(
            description=task_data.description,
            completed=task_data.completed,
            owner_id=self.user_id
        )
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task
    
    def update(self, task_id: int, task_data: TaskBase) -> Optional[Task]:
        """Actualiza una tarea si pertenece al usuario autenticado."""
        db_task = self.get_by_id(task_id)
        if db_task is None:
            return None
        db_task.description = task_data.description
        db_task.completed = task_data.completed
        self.db.commit()
        self.db.refresh(db_task)
        return db_task
    
    def delete(self, task_id: int) -> bool:
        """Elimina una tarea si pertenece al usuario autenticado."""
        db_task = self.get_by_id(task_id)
        if db_task is None:
            return False
        self.db.delete(db_task)
        self.db.commit()
        return Tr