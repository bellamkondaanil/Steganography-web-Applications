
from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import shutil
import os
import uuid
from steganography_module import Steganography

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="../frontend")
app.mount("/assets", StaticFiles(directory="../frontend"), name="assets")

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

steg = Steganography()

@app.post("/process")
async def process_file(method: str = Form(...), operation: str = Form(...), file: UploadFile = Form(...), message: Optional[str] = Form(None)):
    input_path = f"{uuid.uuid4().hex}_{file.filename}"
    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    output_path = f"output_{uuid.uuid4().hex}_{file.filename}"

    try:
        if method == "image":
            if operation == "encode":
                steg.encode_image(input_path, message, output_path)
                return {"success": True, "message": f"Image encoded. Download: {output_path}"}
            else:
                decoded = steg.decode_image(input_path)
                return {"success": True, "message": decoded}

        elif method == "audio":
            if operation == "encode":
                steg.encode_audio(input_path, message, output_path)
                return {"success": True, "message": f"Audio encoded. Download: {output_path}"}
            else:
                decoded = steg.decode_audio(input_path)
                return {"success": True, "message": decoded}

        elif method == "video":
            if operation == "encode":
                steg.encode_video(input_path, message, output_path)
                return {"success": True, "message": f"Video encoded. Download: {output_path}"}
            else:
                decoded = steg.decode_video(input_path)
                return {"success": True, "message": decoded}

        elif method == "text":
            if operation == "encode":
                with open(input_path, 'r', encoding='utf-8') as f:
                    cover = f.read()
                steg.encode_text(cover, message, output_path)
                return {"success": True, "message": f"Text encoded. Download: {output_path}"}
            else:
                decoded = steg.decode_text(input_path)
                return {"success": True, "message": decoded}

        else:
            return {"success": False, "error": "Unsupported method"}
    except Exception as e:
        return {"success": False, "error": str(e)}
