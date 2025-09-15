import uuid
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from redis import Redis
from rq import Queue
from fastapi.responses import FileResponse
from tasks import process_ocr_job

load_dotenv()

origins_env = os.getenv("APP_ORIGINS", "")
allowed_origins = [o.strip() for o in origins_env.split(",") if o.strip()]

app = FastAPI(title=os.getenv("APP_NAME"), version=os.getenv("APP_VERSION"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=[allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexão Redis e fila
redis_conn = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
q = Queue("ocr", connection=redis_conn)

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
async def index():
    return {
        "status": "success",
        "message": f"{os.getenv('APP_NAME')} - v{os.getenv('APP_VERSION')}"
    }


@app.post("/ocr")
async def enqueue_ocr(
    file: UploadFile = File(...),
    lang: str = Form("por+eng"),
    response_type: str = Form("pdf")
):
    # Salva o upload em disco para o worker ler
    tmp_path = UPLOAD_DIR / f"{uuid.uuid4()}_{file.filename}"
    with tmp_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    job = q.enqueue(
        process_ocr_job,
        str(tmp_path),
        lang,
        response_type,
        job_timeout=3600
    )
    return {"task_id": job.get_id(), "status": "queued"}


@app.get("/status/{task_id}")
async def job_status(task_id: str):
    from rq.job import Job
    try:
        job = Job.fetch(task_id, connection=redis_conn)
    except Exception:
        raise HTTPException(status_code=404, detail="Job não encontrado")

    if job.is_queued:
        return {"status": "queued"}
    if job.is_started:
        return {"status": "processing"}
    if job.is_finished:
        result = job.result
        download_url = f"/download/{result['filename_out']}"
        return {"status": "done", "result": result, "download_url": download_url}
    if job.is_failed:
        return {"status": "failed", "error": str(job.exc_info)}


@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=filename
    )
