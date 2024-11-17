from fastapi import FastAPI
from . import models
from .database import engine
from .routers import entities, history, sprints, upload, teams
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:9000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],    
    allow_headers=["*"],   
)

app.include_router(entities.router)
app.include_router(history.router)
app.include_router(sprints.router)
app.include_router(upload.router)
app.include_router(teams.router)