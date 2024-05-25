from fastapi import FastAPI
from src import System

__title__ = "FastAPI Video Streaming Server"

app = System(FastAPI(
    title=__title__
)).app
