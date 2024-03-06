from fastapi import FastAPI, HTTPException, Depends
from app.router import router


app = FastAPI()
