from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.responses import RedirectResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.imagetext import router as image_text_router

app = FastAPI()

@app.get("/", include_in_schema=False,  tags=['docs'])
async def redirect():
    return RedirectResponse("/docs")

app.include_router(image_text_router, prefix="/image-text", tags=["Image Text"])