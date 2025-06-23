# 1. Base image
FROM python:3.12-slim

# 2. Set workdir, copy only requirements and install (cache benefit)
WORKDIR /app
COPY Backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy application code (including Common/)
COPY ../Common ./Common
COPY Backend/utils ./utils
COPY Backend/indexing ./indexing
COPY Backend/database ./database
COPY Backend/data ./data
COPY Backend/api_requests ./api_requests
COPY Backend/api_layer.py .

# 4. Expose FastAPI port
EXPOSE 8000

# 5. Run uvicorn
CMD ["uvicorn", "api_layer:app", "--host", "0.0.0.0", "--port", "8000"]
