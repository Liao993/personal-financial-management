FROM python:3.11.8-slim-bullseye


WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Keep native PDF text extraction lightweight. Pin the 1.x API so installing
# this does not pull newer layout/LLM extras intended for other workflows.
RUN pip install --no-cache-dir "PyMuPDF==1.24.14"

COPY . /app

CMD ["streamlit", "run", "/app/Home.py"]
