import os
import time
import subprocess
import tempfile
from pathlib import Path
from pypdf import PdfReader

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


def process_ocr_job(file_path: str, lang: str, response_type: str):
    """
    Função executada pelo worker RQ.
    Recebe o caminho do arquivo salvo pelo endpoint.
    """
    start = time.perf_counter()

    shared_dir = Path(os.getenv("UPLOAD_DIR", "/shared_uploads"))
    shared_dir.mkdir(parents=True, exist_ok=True)

    original_path = Path(file_path)
    download_name = f"{original_path.stem}_ocr.pdf"
    out_pdf = shared_dir / download_name   # <- grava no volume compartilhado

    run_ocrmypdf(original_path, out_pdf, lang=lang)

    elapsed = round(time.perf_counter() - start, 2)

    if response_type == "json":
        text_ocr = extract_text_with_pypdf(out_pdf)
        pages = len(PdfReader(str(out_pdf)).pages)
        return {
            "status": "done",
            "filename_in": original_path.name,
            "filename_out": download_name,      # apenas o nome do arquivo
            "elapsed_seconds": elapsed,
            "pages": pages,
            "text": text_ocr,
        }
    else:
        return {
            "status": "done",
            "filename_in": original_path.name,
            "filename_out": download_name,
            "elapsed_seconds": elapsed,
        }
