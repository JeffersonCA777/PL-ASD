"""
Ejercicio 1 (Opcional): Autenticación y seguridad.


"""
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Field, Relationship, create_engine, Session, select
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import bcrypt
from typing import Optional, List

app = FastAPI(title="To-Do API con Autenticacion")

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
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    tasks: List["Task"] = Relationship(back_populates="owner")

class TaskBase(SQLModel):
    description: str
    completed: bool = False

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    owner: Optional[User] = Relationship(back_populates="tasks")

class UserData(SQLModel):
    username: str
    password: str

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

DATABASE_URL = "sqlite:///./tareas.db"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as session:
        yield session

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
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
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
    
    def get_all(self) -> List[Task]:
        statement = select(Task).where(Task.owner_id == self.user_id)
        return list(self.db.exec(statement).all())
    
    def get_by_id(self, task_id: int) -> Optional[Task]:
        statement = select(Task).where(
            Task.id == task_id,
            Task.owner_id == self.user_id
        )
        return self.db.exec(statement).first()
    
    def create(self, task_data: TaskBase) -> Task:
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
        db_task = self.get_by_id(task_id)
        if db_task is None:
            return None
        db_task.description = task_data.description
        db_task.completed = task_data.completed
        self.db.commit()
        self.db.refresh(db_task)
        return db_task
    
    def delete(self, task_id: int) -> bool:
        db_task = self.get_by_id(task_id)
        if db_task is None:
            return False
        self.db.delete(db_task)
        self.db.commit()
        return True

def get_repo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TaskRepository:
    return TaskRepository(db, current_user.id)

@app.post("/users", status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: UserData,
    db: Session = Depends(get_db)
):
    hashed_pwd = get_password_hash(user_in.password)
    db_user = User(username=user_in.username, hashed_password=hashed_pwd)
    try:
        db.add(db_user)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    return {"msg": "User created"}

@app.post("/token", response_model=Token)
def login_for_access_token(
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
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@app.get("/tasks", response_model=List[Task])
def list_tasks(repo: TaskRepository = Depends(get_repo)):
    return repo.get_all()

@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskBase,
    repo: TaskRepository = Depends(get_repo)
):
    return repo.create(task_data)

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    repo: TaskRepository = Depends(get_repo)
):
    task = repo.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task_data: TaskBase,
    repo: TaskRepository = Depends(get_repo)
):
    task = repo.update(task_id, task_data)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    repo: TaskRepository = Depends(get_repo)
):
    if not repo.delete(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return None

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)