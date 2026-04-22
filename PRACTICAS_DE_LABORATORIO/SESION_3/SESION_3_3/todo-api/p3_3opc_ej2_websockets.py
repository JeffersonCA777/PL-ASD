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