FROM python:3.11-bullseye

WORKDIR /app

COPY docker/requirements_app.txt /tmp/requirements_app.txt
RUN pip install --no-cache-dir -r /tmp/requirements_app.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "新建案制震產品統計.py", \
     "--server.headless", "true", \
     "--server.port", "8501", \
     "--server.enableCORS", "false", \
     "--server.enableXsrfProtection", "false"]
