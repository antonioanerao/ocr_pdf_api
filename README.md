# OCR arquivos do SAJ

<a href="https://github.com/mp-ac/ocr_pdf_api/actions"><img src="https://github.com/mp-ac/ocr_pdf_api/actions/workflows/docker-image.yml/badge.svg" alt="Docker Image Build"></a>

### MacOS
qpdf<br>
poppler<br>
ocrmypdf<br>
tesseract<br>
tesseract-lang

#### Instalacao

```bash
brew install qpdf poppler ocrmypdf tesseract tesseract-lang
```

### Linux (Debian/Ubuntu)

qpdf<br>
poppler-utils<br>
ocrmypdf<br>
tesseract-ocr<br>
tesseract-ocr-por<br>
tesseract-ocr-eng

#### Instalacao

```bash
sudo apt update
sudo apt install -y qpdf poppler-utils ocrmypdf tesseract-ocr tesseract-ocr-por tesseract-ocr-eng
```

## Testes de desempenho


| Configuração                  | Jobs simultâneos | Tempo médio (s) |
|-------------------------------|------------------|-----------------|
| **2 réplicas × 1 CPU**        | 1 job           | ~54            |
|                               | 2 jobs          | ~40            |
| **2 réplicas × 2 CPU**        | 1 job           | ~18.6          |
|                               | 2 jobs          | ~17            |
| **2 réplicas × 3 CPU**        | 1 job           | ~12.6          |
|                               | 2 jobs          | ~13.5          |
| **2 réplicas × 8 CPU**        | 1 job           | ~9.2           |
|                               | 2 jobs          | ~12            |
| **3 réplicas × 2 CPU**        | 1 job           | ~18.7          |
|                               | 2 jobs          | ~17.0          |
|                               | 3 jobs          | ~18.5          |

### Dimensionamento recomendado

Os testes mostram que **2 vCPU por worker** oferece o melhor equilíbrio entre tempo de processamento e uso de recursos.

* **Tempo médio por PDF:** ~18 s  
* **Escalabilidade:** aumente o throughput adicionando mais réplicas do worker em vez de adicionar mais CPUs a cada contêiner.
* **Resumo:** *mais réplicas de 2 vCPU* ⇒ maior volume processado mantendo tempo estável.

### Aumento no tempo de OCR

Os testes anteriores foram em um PDF de 169Kb com 5 páginas. O tempo cresce quase proporcional ao número de páginas. Um teste realizado em um arquivo de 132 páginas com total de 19Mb demorou um total de 744 segundos (12 minutos e 24 segundos) sendo 3 réplicas de 2x CPU (3 jobs simultâneos).
