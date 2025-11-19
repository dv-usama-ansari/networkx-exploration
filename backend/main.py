from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from graph_router import graph_router

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graph_router)


@app.get("/")
def hello_world():
    return {"message": "Hello, World!"}
