# Bus Management API (Flask)

REST API для управління автобусними маршрутами з повною підтримкою Azure SQL Database та Swagger документацією.

## 📋 Зміст

- [Особливості](#особливості)
- [Локальний запуск](#локальний-запуск)
- [Розгортання на Azure](#розгортання-на-azure)
- [API Документація](#api-документація)
- [Доступні Endpoints](#доступні-endpoints)

## ✨ Особливості

- ✅ Повна CRUD функціональність для автобусів, маршрутів, зупинок, водіїв та оглядів
- ✅ Підтримка Azure SQL Database
- ✅ Підтримка MySQL (локальна розробка)
- ✅ Swagger/OpenAPI документація
- ✅ Health check endpoint
- ✅ Збережені процедури та статистика
- ✅ Готовий до розгортання на Azure App Service

## 🚀 Локальний запуск

### Вимоги

- Python 3.11+
- MySQL (для локальної розробки) або доступ до Azure SQL Database

### Інсталяція

```bash
# Клонувати репозиторій
git clone <your-repo-url>
cd database-Flask

# Створити віртуальне середовище
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Встановити залежності
pip install -r requirements.txt
```

### Налаштування змінних оточення

**Для MySQL (локальна розробка):**

```bash
export DB_DRIVER=mysql
export DB_HOST=localhost
export DB_PORT=3306
export DB_USERNAME=root
export DB_PASSWORD=your_password
export DB_NAME=bus
```

**Для Azure SQL Database:**

```bash
export DB_DRIVER=mssql+pyodbc
export DB_HOST=your-server.database.windows.net
export DB_PORT=1433
export DB_USERNAME=your-admin-username
export DB_PASSWORD=your-secure-password
export DB_NAME=bus
export ODBC_DRIVER="ODBC Driver 18 for SQL Server"
```

**Альтернативно - один рядок підключення:**

```bash
export DATABASE_URL="mssql+pyodbc://username:password@your-server.database.windows.net:1433/bus?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no&Connection+Timeout=30"
```

### Запуск

```bash
python app.py
# Відкрийте http://localhost:5000/apidocs для Swagger UI
# Health check: http://localhost:5000/healthz
```

## ☁️ Розгортання на Azure

### Крок 1: Підготовка Azure ресурсів

1. **Створіть Azure SQL Database:**

   ```bash
   # Через Azure Portal або Azure CLI
   az sql server create --name <server-name> --resource-group <rg-name> \
     --location eastus --admin-user <admin-user> --admin-password <password>

   az sql db create --resource-group <rg-name> --server <server-name> \
     --name bus --service-objective S0
   ```

2. **Налаштуйте firewall правила:**

   - Додайте IP адресу вашої віртуальної машини
   - Або дозвольте Azure services: `Allow Azure services and resources to access this server`

3. **Створіть структуру БД:**
   - Підключіться до БД через SSMS, Azure Data Studio або sqlcmd
   - Виконайте SQL скрипт створення таблиць, тригерів та процедур

### Крок 2: Розгортання на віртуальній машині Azure

1. **Підключіться до віртуальної машини:**

   ```bash
   ssh azureuser@<vm-ip-address>
   ```

2. **Встановіть необхідне ПЗ:**

   ```bash
   # Оновити систему
   sudo apt update && sudo apt upgrade -y

   # Встановити Python 3.11 (через deadsnakes PPA)
   sudo apt install software-properties-common -y
   sudo add-apt-repository ppa:deadsnakes/ppa -y
   sudo apt update
   sudo apt install python3.11 python3.11-venv python3.11-dev python3-pip -y

   # АБО використати Python 3.10 (якщо вже встановлений)
   # python3 --version  # перевірити версію
   # sudo apt install python3-venv python3-pip -y

   # Встановити ODBC Driver для SQL Server
   curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
   curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | \
     sudo tee /etc/apt/sources.list.d/mssql-release.list
   sudo apt update
   sudo ACCEPT_EULA=Y apt install -y msodbcsql18 unixodbc-dev g++

   # Встановити Git
   sudo apt install git -y
   ```

3. **Клонувати та налаштувати проект:**

   ```bash
   # Клонувати репозиторій
   git clone https://github.com/volodiagamivka/db-repo.git
   cd db-repo

   # Створити віртуальне середовище (Python 3.11)
   python3.11 -m venv .venv
   source .venv/bin/activate

   # АБО якщо використовуєте Python 3.10
   # python3 -m venv .venv
   # source .venv/bin/activate

   # Оновити pip
   pip install --upgrade pip

   # Встановити залежності
   pip install -r requirements.txt
   ```

4. **Налаштувати змінні оточення:**

   ```bash
   # Створити файл .env
   nano .env
   ```

   Додати наступний вміст (з вашими даними):

   ```
   DB_DRIVER=mssql+pyodbc
   DB_HOST=your-server.database.windows.net
   DB_PORT=1433
   DB_USERNAME=your-admin-username
   DB_PASSWORD=your-secure-password
   DB_NAME=bus
   ODBC_DRIVER=ODBC Driver 18 for SQL Server
   FLASK_ENV=production
   ```

5. **Запустити додаток:**

   **Використовуючи startup.sh:**

   ```bash
   chmod +x startup.sh
   ./startup.sh
   ```

   **Або вручну з gunicorn:**

   ```bash
   gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 600 app:app
   ```

6. **Налаштувати systemd для автозапуску:**

   ```bash
   sudo nano /etc/systemd/system/busapi.service
   ```

   Додати (замініть `azureuser` на ваше ім'я користувача):

   ```ini
   [Unit]
   Description=Bus Management API
   After=network.target

   [Service]
   User=azureuser
   WorkingDirectory=/home/azureuser/db-repo
   Environment="PATH=/home/azureuser/db-repo/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
   EnvironmentFile=/home/azureuser/db-repo/.env
   ExecStart=/home/azureuser/db-repo/.venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 600 app:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Запустити сервіс:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable busapi
   sudo systemctl start busapi
   sudo systemctl status busapi
   ```

7. **Налаштувати Nginx як reverse proxy (опціонально):**

   ```bash
   sudo apt install nginx -y
   sudo nano /etc/nginx/sites-available/busapi
   ```

   Додати:

   ```nginx
   server {
       listen 80;
       server_name <your-vm-ip-or-domain>;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```

   Активувати:

   ```bash
   sudo ln -s /etc/nginx/sites-available/busapi /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### Крок 3: Відкрити порти

```bash
# Відкрити порт 8000 (або 80 якщо використовуєте Nginx)
sudo ufw allow 8000
# або для Nginx:
sudo ufw allow 80
sudo ufw allow 443  # для HTTPS
sudo ufw enable
```

В Azure Portal також додайте правило в Network Security Group:

- Inbound rule для порту 80 (HTTP) та/або 8000

## 📚 API Документація

Swagger UI доступний за адресою: `/apidocs`

Після розгортання:

- **Локально:** http://localhost:5000/apidocs
- **Azure VM:** http://\<your-vm-ip\>/apidocs

Health check endpoint: `/healthz`

## 🔌 Доступні Endpoints

### Buses (Автобуси)

- `GET /buses` - Отримати всі автобуси
- `GET /buses/{id}` - Отримати автобус за ID
- `POST /buses` - Створити новий автобус
- `PUT /buses/{id}` - Оновити автобус
- `DELETE /buses/{id}` - Видалити автобус
- `GET /routes/{route_id}/buses` - Отримати автобуси за маршрутом

### Routes (Маршрути)

- `GET /routes` - Отримати всі маршрути
- `GET /routes/{id}` - Отримати маршрут за ID
- `POST /routes` - Створити новий маршрут
- `PUT /routes/{id}` - Оновити маршрут
- `DELETE /routes/{id}` - Видалити маршрут
- `POST /routes/insert` - Додати записи до маршруту

### Stops (Зупинки)

- `GET /stops` - Отримати всі зупинки
- `GET /stops/{id}` - Отримати зупинку за ID
- `POST /stops` - Створити нову зупинку
- `PUT /stops/{id}` - Оновити зупинку
- `DELETE /stops/{id}` - Видалити зупинку

### Route Stops (Зупинки маршрутів)

- `GET /route_stops` - Отримати всі зупинки маршрутів
- `GET /route_stops/{id}` - Отримати зупинку маршруту за ID
- `POST /route_stops` - Створити зупинку маршруту
- `PUT /route_stops/{id}` - Оновити зупинку маршруту
- `DELETE /route_stops/{id}` - Видалити зупинку маршруту
- `GET /route_stops/route/{route_id}` - Отримати зупинки за маршрутом
- `POST /route_stop` - Вставити зупинку до маршруту (збережена процедура)

### Drivers (Водії)

- `GET /drivers` - Отримати всіх водіїв
- `GET /drivers/{id}` - Отримати водія за ID
- `POST /drivers` - Створити нового водія
- `PUT /drivers/{id}` - Оновити водія
- `DELETE /drivers/{id}` - Видалити водія
- `GET /drivers/stats` - Отримати статистику по водіях

### Bus Inspections (Огляди автобусів)

- `GET /inspections` - Отримати всі огляди
- `GET /inspections/{id}` - Отримати огляд за ID
- `POST /inspections` - Створити новий огляд
- `PUT /inspections/{id}` - Оновити огляд
- `DELETE /inspections/{id}` - Видалити огляд
- `GET /buses/{bus_id}/inspections` - Отримати огляди за автобусом

### Statistics (Статистика)

- `GET /aggregate` - Отримати агрегатну статистику
  - Query params: `table_name`, `column_name`, `operation` (SUM, AVG, MAX, MIN, COUNT)

### Database (База даних)

- `POST /create-db` - Створити структуру бази даних

## 🔧 Налаштування

Додаток читає конфігурацію з змінних оточення:

### Обов'язкові змінні:

- `DB_DRIVER` - Драйвер БД (`mysql` або `mssql+pyodbc`)
- `DB_HOST` - Хост БД
- `DB_PORT` - Порт БД
- `DB_USERNAME` - Ім'я користувача БД
- `DB_PASSWORD` - Пароль БД
- `DB_NAME` - Назва БД

### Опціональні змінні:

- `DATABASE_URL` - Повний рядок підключення (замість окремих параметрів)
- `ODBC_DRIVER` - Драйвер ODBC для Azure SQL (за замовчуванням: "ODBC Driver 18 for SQL Server")
- `FLASK_ENV` - Середовище Flask (`development` або `production`)

## 📝 Примітки

- Проект використовує SQLAlchemy для роботи з БД
- Підтримуються як MySQL так і Azure SQL Database
- Всі endpoints зареєстровані як Flask blueprints
- Connection pooling налаштований для Azure SQL
- Swagger документація генерується автоматично з docstrings

## 🔍 Troubleshooting

### Проблема з підключенням до Azure SQL:

```bash
# Перевірте firewall правила
# Перевірте чи встановлений ODBC Driver 18
odbcinst -j
```

### Проблема з gunicorn:

```bash
# Перевірте логи
sudo journalctl -u busapi -f
```

### Проблема з портами:

```bash
# Перевірте чи порт відкритий
sudo netstat -tlnp | grep 8000
```

## 📄 Ліцензія

Цей проект створений для навчальних цілей.
