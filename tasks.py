import time
import shutil
import subprocess
import tempfile
from pathlib import Path
from pypdf import PdfReader
from fastapi.responses import JSONResponse


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
    tmpdir = Path(tempfile.mkdtemp())

    original_path = Path(file_path)
    download_name = f"{original_path.stem}_ocr.pdf"
    out_pdf = tmpdir / download_name

    run_ocrmypdf(original_path, out_pdf, lang=lang)

    elapsed = round(time.perf_counter() - start, 2)

    if response_type == "json":
        text_ocr = extract_text_with_pypdf(out_pdf)
        pages = len(PdfReader(str(out_pdf)).pages)
        return {
            "status": "done",
            "filename_in": original_path.name,
            "filename_out": download_name,
            "pages": pages,
            "elapsed_seconds": elapsed,
            "text": text_ocr,
        }
    else:
        # Retorne só o caminho do PDF gerado (poderia mover para storage definitivo)
        return {
            "status": "done",
            "filename_in": original_path.name,
            "filename_out": str(out_pdf),
            "elapsed_seconds": elapsed,
        }
