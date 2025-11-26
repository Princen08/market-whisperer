FROM python:3.10-slim

WORKDIR /app

# install requirements from the repo's backend folder (build with repo root as context)
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# copy the whole backend folder into /app/backend
COPY backend/ /app/backend/

# run from the backend folder and ensure Python finds modules there
WORKDIR /app/backend

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]