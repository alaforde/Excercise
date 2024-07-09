from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import os
import json
from concurrent.futures import ThreadPoolExecutor

router = APIRouter()

output_dir = "static"
data_dir = "data"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(data_dir, exist_ok=True)

text_inputs_path = os.path.join(data_dir, "text_inputs.json")

def read_text_inputs():
    if os.path.exists(text_inputs_path):
        with open(text_inputs_path, "r") as f:
            return json.load(f)
    return []

def save_text_inputs(text_inputs):
    with open(text_inputs_path, "w") as f:
        json.dump(text_inputs, f)

@router.post("/add-text")
async def add_text_to_image(file: UploadFile = File(...), text: str = ""):
    if len(text) > 20:
        raise HTTPException(status_code=400, detail="Text length exceeds 20 characters")
    
    if file.content_type.split("/")[0] != "image":
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    if file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB")
    
    try:
        with ThreadPoolExecutor(max_workers=3) as executor:
            output_path = executor.submit(save_image_with_text, file, text).result()
        
        with open(output_path, "rb") as img_file:
            base64_img = base64.b64encode(img_file.read()).decode("utf-8")
        
        return {"base64_image": base64_img, "image_url": f"/image-text/static/{os.path.basename(output_path)}"}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/texts")
async def get_texts():
    text_inputs = read_text_inputs()
    return {"texts": [entry["text"] for entry in text_inputs]}

@router.get("/check-text")
async def check_text(text: str):
    text_inputs = read_text_inputs()
    for entry in text_inputs:
        if entry["text"] == text:
            return {"exists": True, "image_url": f"/image-text/static/{os.path.basename(entry['path'])}"}
    return {"exists": False}

# Serve static files
from fastapi.staticfiles import StaticFiles
router.mount("/static", StaticFiles(directory=output_dir), name="static")
