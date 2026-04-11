# используем официальный образ Python
FROM python:3.11-slim

# устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# копируем файл с зависимостями
COPY requirements.txt .

# устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# копируем код
COPY app/ ./app/
COPY data/ ./data/

# открываем порт
EXPOSE 8000

# команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]