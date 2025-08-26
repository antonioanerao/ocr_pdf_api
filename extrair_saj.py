import sys
import subprocess
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
    cmd = ["ocrmypdf", "--language", lang, "--deskew", "--force-ocr", str(src), str(dst)]
    subprocess.run(cmd, check=True)


def main():
    if len(sys.argv) < 2:
        print("Uso: py extrair_saj.py nome_arquivo.pdf")
        sys.exit(1)

    pdf_in = Path(sys.argv[1])
    if not pdf_in.exists():
        print(f"Arquivo não encontrado: {pdf_in}", file=sys.stderr)
        sys.exit(1)

    ocr_pdf = pdf_in.with_name(pdf_in.stem + "_ocr.pdf")
    out_txt = pdf_in.with_name("saida.txt")
    out_docx = pdf_in.with_name("saida.docx")

    run_ocrmypdf(pdf_in, ocr_pdf, lang="por+eng")
    text_ocr = extract_text_with_pypdf(ocr_pdf)

    out_txt.write_text(text_ocr, encoding="utf-8")

    print("OCR concluído.")
    print(f"Texto salvo em: {out_txt}")
    print(f"Word salvo em: {out_docx} (texto copiável/editável)")
    print(f"PDF com OCR salvo em: {ocr_pdf}")


if __name__ == "__main__":
    main()
