FROM python:3.10-slim

WORKDIR /app

# install requirements from the build context (when building inside backend/)
COPY requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# copy the whole backend folder into /app/backend
COPY . /app/backend/

# run from the backend folder and ensure Python finds modules there
WORKDIR /app/backend
ENV PYTHONPATH=.

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]