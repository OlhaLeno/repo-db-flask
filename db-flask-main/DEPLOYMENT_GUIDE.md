# Інструкції з розгортання на Azure VM

## Проблема: Unable to locate package python3.11

Якщо ви отримуєте помилку при встановленні Python 3.11, виконайте наступні кроки:

### Рішення 1: Використати deadsnakes PPA (рекомендовано для Ubuntu)

```bash
# Додати PPA репозиторій
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Встановити Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev python3-pip -y

# Перевірити встановлення
python3.11 --version
```

### Рішення 2: Використати наявну версію Python

Якщо Python 3.10 вже встановлений (перевірте з `python3 --version`):

```bash
# Встановити необхідні пакети для Python 3.10
sudo apt install python3 python3-venv python3-pip python3-dev -y

# Під час налаштування проекту використовуйте:
python3 -m venv .venv
source .venv/bin/activate
```

**Важливо:** Проект працює з Python 3.9+, тому Python 3.10 цілком підійде.

### Рішення 3: Встановити з source (якщо PPA не працює)

```bash
# Встановити залежності для компіляції
sudo apt update
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev \
  libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev -y

# Завантажити та встановити Python 3.11
cd /tmp
wget https://www.python.org/ftp/python/3.11.6/Python-3.11.6.tgz
tar -xf Python-3.11.6.tgz
cd Python-3.11.6
./configure --enable-optimizations
make -j $(nproc)
sudo make altinstall

# Перевірити
python3.11 --version
```

## Повний процес розгортання (покрокова інструкція)

### Крок 1: Підключення та оновлення системи

```bash
# Підключитися до VM
ssh azureuser@<your-vm-ip>

# Оновити систему
sudo apt update && sudo apt upgrade -y
```

### Крок 2: Встановлення Python

**Варіант A: Python 3.11 через PPA**
```bash
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev -y
```

**Варіант B: Використати системний Python 3.10**
```bash
sudo apt install python3 python3-venv python3-pip python3-dev -y
```

### Крок 3: Встановлення ODBC драйвера для SQL Server

```bash
# Додати Microsoft репозиторій
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -

# Для Ubuntu (перевірте версію: lsb_release -rs)
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | \
  sudo tee /etc/apt/sources.list.d/mssql-release.list

sudo apt update

# Встановити ODBC драйвер
sudo ACCEPT_EULA=Y apt install -y msodbcsql18 unixodbc-dev g++

# Перевірити встановлення
odbcinst -j
```

### Крок 4: Клонування та налаштування проекту

```bash
# Встановити Git (якщо ще не встановлено)
sudo apt install git -y

# Клонувати репозиторій
git clone https://github.com/volodiagamivka/db-repo.git
cd db-repo

# Створити віртуальне середовище
# Для Python 3.11:
python3.11 -m venv .venv
# АБО для системного Python:
# python3 -m venv .venv

# Активувати віртуальне середовище
source .venv/bin/activate

# Оновити pip
pip install --upgrade pip

# Встановити залежності
pip install -r requirements.txt
```

### Крок 5: Налаштування змінних оточення

```bash
# Створити файл .env
nano .env
```

Додати наступний вміст (замініть на ваші дані):

```env
DB_DRIVER=mssql+pyodbc
DB_HOST=your-server.database.windows.net
DB_PORT=1433
DB_USERNAME=your-admin-username
DB_PASSWORD=your-secure-password
DB_NAME=bus
ODBC_DRIVER=ODBC Driver 18 for SQL Server
FLASK_ENV=production
```

Зберегти файл: `Ctrl+O`, `Enter`, `Ctrl+X`

### Крок 6: Тестовий запуск

```bash
# Переконатися що .venv активовано
source .venv/bin/activate

# Перевірити що всі залежності встановлено
pip list | grep gunicorn

# Якщо gunicorn не встановлено - перевстановити залежності
pip install -r requirements.txt

# Запустити додаток для тестування
python app.py
```

АБО з Gunicorn (рекомендовано для production):
```bash
# Використовуючи startup.sh (автоматично активує venv)
chmod +x startup.sh
./startup.sh

# АБО вручну з віртуального середовища
.venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 600 app:app
```

**ВАЖЛИВО:** Завжди використовуйте gunicorn з віртуального середовища (`.venv/bin/gunicorn`), 
а не системний gunicorn!

Відкрити в браузері: `http://<vm-ip>:8000/apidocs`

### Крок 7: Налаштування автозапуску (systemd)

```bash
# Створити systemd service файл
sudo nano /etc/systemd/system/busapi.service
```

Додати:

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

### Крок 8: Налаштування firewall

```bash
# Відкрити порт 8000
sudo ufw allow 8000
sudo ufw enable
sudo ufw status
```

**Важливо:** В Azure Portal також додайте правило в Network Security Group для порту 8000.

### Крок 9 (Опціонально): Налаштування Nginx

```bash
# Встановити Nginx
sudo apt install nginx -y

# Створити конфігурацію
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

# Відкрити порт 80
sudo ufw allow 80
```

## Корисні команди для діагностики

```bash
# Перевірити статус сервісу
sudo systemctl status busapi

# Переглянути логи
sudo journalctl -u busapi -f

# Перезапустити сервіс
sudo systemctl restart busapi

# Перевірити відкриті порти
sudo netstat -tlnp | grep 8000

# Перевірити підключення до Azure SQL
odbcinst -j
tsql -S your-server.database.windows.net -U your-username -P your-password

# Тестувати API
curl http://localhost:8000/healthz
```

## Можливі проблеми та рішення

### Помилка: "gunicorn: command not found" або "ModuleNotFoundError"

```bash
# Переконатися що віртуальне середовище активовано
source .venv/bin/activate

# Перевірити що активовано правильне середовище
which python
# Має показати: /home/azureuser/db-repo/.venv/bin/python

# Оновити pip та встановити залежності
pip install --upgrade pip
pip install -r requirements.txt

# Перевірити встановлення gunicorn
which gunicorn
gunicorn --version

# Якщо все ще помилка - встановити gunicorn окремо
pip install gunicorn
```

### Помилка підключення до Azure SQL

1. Перевірте firewall правила в Azure Portal
2. Додайте IP адресу VM до дозволених
3. Перевірте чи правильні дані підключення в `.env`

### Порт вже використовується

```bash
# Знайти процес який використовує порт
sudo lsof -i :8000

# Завершити процес
sudo kill -9 <PID>
```

### Сервіс не запускається

```bash
# Переглянути детальні логи
sudo journalctl -u busapi -n 50 --no-pager

# Перевірити права доступу
ls -la /home/azureuser/db-repo
```

## Оновлення коду

```bash
cd /home/azureuser/db-repo
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart busapi
```

## Підсумок

Після виконання всіх кроків:
- ✅ Swagger UI доступний на `http://<vm-ip>:8000/apidocs` (або `http://<vm-ip>/apidocs` з Nginx)
- ✅ Health check: `http://<vm-ip>:8000/healthz`
- ✅ Сервіс автоматично запускається при перезавантаженні VM
- ✅ Підключення до Azure SQL Database налаштовано

