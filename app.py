import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader

app = FastAPI(title="OCR API", version="1.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8001",],  # ajuste
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_with_pypdf(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    texts = []
    for page in reader.pages:
        try:
            t = page.extract_text() or ""
        except Exception:
            t = ""
        texts.append(t.strip())
    return "\n\n".join(texts)


def run_ocrmypdf(src: Path, dst: Path, lang: str = "por+eng") -> None:
    cmd = [
        "ocrmypdf",
        "--language", lang,
        "--deskew",
        "--optimize", "1",
        "--force-ocr",
        str(src),
        str(dst),
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            f"OCR falhou (code {completed.returncode}). "
            f"stderr: {completed.stderr.strip() or 'sem stderr'}"
        )


@app.post("/ocr")
async def ocr_endpoint(
    file: UploadFile = File(..., description="PDF para OCR"),
    lang: str = Form("por+eng"),
    response_type: Literal["json", "pdf"] = Form("pdf"),
):
    ct = (file.content_type or "").lower()
    if ct not in {"application/pdf", "application/x-pdf", "application/octet-stream"}:
        raise HTTPException(status_code=400, detail=f"Tipo de arquivo não suportado: {ct or 'desconhecido'}")

    try:
        start_time = time.perf_counter()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Nome do arquivo de saída
            original_name = file.filename or "arquivo.pdf"
            original_stem = Path(original_name).stem or "arquivo"
            download_name = f"{original_stem}_ocr.pdf"

            in_path = tmpdir / "entrada.pdf"
            out_pdf = tmpdir / download_name

            # Salva upload no disco
            with in_path.open("wb") as f:
                shutil.copyfileobj(file.file, f)

            # Executa OCR
            run_ocrmypdf(in_path, out_pdf, lang=lang)

            elapsed = round(time.perf_counter() - start_time, 2)  # segundos

            if response_type == "json":
                text_ocr = extract_text_with_pypdf(out_pdf)
                pages = len(PdfReader(str(out_pdf)).pages)
                return JSONResponse(
                    {
                        "filename_in": original_name,
                        "filename_out": download_name,
                        "lang": lang,
                        "pages": pages,
                        "elapsed_seconds": elapsed,
                        "text": text_ocr,
                    }
                )

            # PDF como resposta
            headers = {
                "Content-Disposition": f'attachment; filename="{download_name}"',
                "X-Original-Filename": original_name,
                "X-Processing-Time": f"{elapsed}s",
            }
            return StreamingResponse(out_pdf.open("rb"), media_type="application/pdf", headers=headers)

    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {e}")
