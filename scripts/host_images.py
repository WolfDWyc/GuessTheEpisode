import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

PORT = 8001
FRAMES_PATH = "../frames-prod"

app = FastAPI()
app.mount("/images", StaticFiles(directory=FRAMES_PATH), name="images")

if __name__ == '__main__':
    uvicorn.run(app, port=PORT)
