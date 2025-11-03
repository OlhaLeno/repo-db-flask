# 1. Базовий образ Python
FROM python:3.10-slim

# 2. Встановлюємо робочу директорію
WORKDIR /app

# 3. Копіюємо файл залежностей
COPY requirements.txt requirements.txt

# 4. Встановлюємо залежності
RUN pip install -r requirements.txt

# 5. Копіюємо весь код проекту в контейнер
COPY . .

# 6. Вказуємо порт (той самий, що в azure-deploy.sh - target-port 5000)
EXPOSE 5000

# 7. Запускаємо Gunicorn (стандарт для production)
# 'app:app' означає: у файлі 'app.py' шукай змінну 'app'
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "db-flask-main", "app:app"]