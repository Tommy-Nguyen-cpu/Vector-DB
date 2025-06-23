# 1. Base image
FROM python:3.12-slim

# 2. Workdir and install Streamlit + requests + Common dep
WORKDIR /app
COPY Frontend/SimpleUI/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy the UI code and shared schemas
COPY Frontend/SimpleUI/ui.py .
COPY ../../Common ./Common

# 4. Expose Streamlit port
EXPOSE 8501

# 5. Entrypoint to Streamlit
ENTRYPOINT ["streamlit", "run", "ui.py", "--server.address=0.0.0.0"]
