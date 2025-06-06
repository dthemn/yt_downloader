import subprocess
import uuid
import os

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Serve static files if you add css/js later
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def run_cmd(cmd):
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


# Home page with input form
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Endpoint to handle form submission
@app.post("/download", response_class=HTMLResponse)
async def download(request: Request, url: str = Form(...)):
    raw_output = run_cmd(["yt-dlp", "-g", url])
    lines = raw_output.splitlines()
    if len(lines) != 2:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "message": "Failed to get video/audio URLs. Try again or check URL.",
            },
        )

    video_url, audio_url = lines
    filename = f"output_{uuid.uuid4().hex[:8]}.mp4"
    filepath = os.path.join(OUTPUT_DIR, filename)

    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_url,
        "-i",
        audio_url,
        "-c",
        "copy",
        filepath,
    ]

    ffmpeg_output = run_cmd(ffmpeg_cmd)
    if not os.path.exists(filepath):
        return templates.TemplateResponse(
            "error.html", {"request": request, "message": "Merging failed."}
        )

    return templates.TemplateResponse(
        "result.html", 
        {"request": request, "url": url, "filename": filename}
    )


@app.get("/downloaded/{filename}")
async def serve_file(filename: str):
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        return {"error": "File not found."}
    return FileResponse(filepath, media_type="video/mp4", filename=filename)
