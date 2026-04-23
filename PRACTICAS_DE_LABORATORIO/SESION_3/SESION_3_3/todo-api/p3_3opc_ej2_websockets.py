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
