FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
PYTHONUNBUFFERED=1
COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install build && python -m build --wheel --no-isolation || true
COPY . .
RUN pip install -e .
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
