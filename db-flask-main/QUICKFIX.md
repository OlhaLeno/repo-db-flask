# 🚀 QUICKFIX - Швидке виправлення проблем

## ⚡ Швидкий старт

```bash
# 1. Клонувати репозиторій
git clone https://github.com/volodiagamivka/db-repo.git
cd db-repo

# 2. Створити віртуальне середовище
python3 -m venv .venv
source .venv/bin/activate

# 3. Встановити залежності
pip install -r requirements.txt

# 4. Створити .env файл
nano .env
```

**Вміст .env файлу:**

```env
DB_HOST=cloud-serverrs.mysql.database.azure.com
DB_USER=olhalenyo
DB_PASSWORD=Lenyo2006
DB_NAME=bus
SECRET_KEY=a901d7d59e5510b5513174f8350d78bd7ae0c1b08ff7ebade7d8bc8223314c2f
FLASK_ENV=production
```

```bash
# 5. Створити таблиці
python3 create_tables.py

# 6. Запустити додаток
./startup.sh
```

## ❌ Помилка: `gunicorn: command not found` або `ModuleNotFoundError: No module named 'flask'`

**Причина:** Gunicorn запускається з системного Python, а не з віртуального середовища

**Рішення 1 (Швидке):**

```bash
# На Azure VM
cd ~/db-repo
source .venv/bin/activate

# Встановити залежності
pip install --upgrade pip
pip install -r requirements.txt

# Запустити gunicorn з віртуального середовища
.venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 600 app:app
```

**Рішення 2 (Оновити startup.sh):**

```bash
# Оновити startup.sh з GitHub
git pull origin main

# Зробити виконуваним
chmod +x startup.sh

# Запустити
./startup.sh
```

---

## ❌ Помилка: `Unable to locate package python3.11`

**Причина:** Python 3.11 немає в стандартних репозиторіях Ubuntu

**Рішення:**

```bash
# Додати PPA репозиторій
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev -y
```

**АБО використати Python 3.10:**

```bash
python3 --version  # перевірити версію
sudo apt install python3 python3-venv python3-pip python3-dev -y
python3 -m venv .venv
```

---

## ❌ Помилка: `pkg-config: not found` або помилка компіляції `mysqlclient`

**Причина:** `mysqlclient` не потрібен для Azure SQL Database

**Рішення 1 (Оновити requirements.txt з GitHub):**

```bash
cd ~/db-repo
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
```

**Рішення 2 (Видалити MySQL залежності вручну):**

```bash
# Відредагувати requirements.txt і закоментувати/видалити:
# Flask-MySQLdb==2.0.0
# mysqlclient==2.2.4

source .venv/bin/activate
pip install -r requirements.txt
```

---

## ❌ Помилка: `ModuleNotFoundError: No module named 'pyodbc'`

**Рішення:**

```bash
# Встановити системні залежності
sudo apt install unixodbc-dev g++ -y

# Встановити Python пакети
source .venv/bin/activate
pip install --upgrade pip
pip install pyodbc pymssql
```

---

## ❌ Помилка підключення до Azure SQL Database

**Перевірити:**

1. **Firewall правила в Azure Portal:**

   - SQL Server → Networking → Firewall rules
   - Додайте IP адресу вашої VM

2. **Connection string:**

   ```bash
   cat .env  # перевірити налаштування
   ```

3. **ODBC Driver:**
   ```bash
   odbcinst -j  # має показати ODBC Driver 18 for SQL Server
   ```

---

## ❌ Порт 8000 вже використовується

**Рішення:**

```bash
# Знайти процес
sudo lsof -i :8000

# Завершити процес
sudo kill -9 <PID>

# АБО використати інший порт
gunicorn --bind 0.0.0.0:8080 --workers 4 app:app
```

---

## ❌ Сервіс не запускається (systemd)

**Діагностика:**

```bash
# Переглянути статус
sudo systemctl status busapi

# Переглянути логи
sudo journalctl -u busapi -n 50 --no-pager

# Перевірити права доступу
ls -la ~/db-repo

# Перезапустити
sudo systemctl restart busapi
```

---

## ✅ Швидкий старт (все працює)

```bash
cd ~/db-repo
source .venv/bin/activate

# Створити .env файл
cat > .env << 'EOF'
DB_HOST=your-server.database.windows.net
DB_USER=your-admin-username
DB_PASSWORD=your-password
DB_NAME=bus
SECRET_KEY=your-secret-key-change-this
FLASK_ENV=production
EOF

# Відредагувати .env з вашими даними
nano .env

# Встановити залежності та запустити
pip install -r requirements.txt
.venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 600 app:app
```

Відкрити: `http://<vm-ip>:8000/apidocs`

---

## 📋 Корисні команди

```bash
# Перевірити статус
sudo systemctl status busapi

# Переглянути логи в реальному часі
sudo journalctl -u busapi -f

# Перезапустити сервіс
sudo systemctl restart busapi

# Перевірити відкриті порти
sudo netstat -tlnp | grep 8000

# Тестувати API
curl http://localhost:8000/healthz

# Оновити код
git pull origin main
pip install -r requirements.txt
sudo systemctl restart busapi
```

---

## 🔧 Повне переналаштування

Якщо нічого не працює - почати з чистого аркуша:

```bash
# Видалити віртуальне середовище
cd ~/db-repo
rm -rf .venv

# Створити знову
python3.11 -m venv .venv
# АБО: python3 -m venv .venv

# Активувати
source .venv/bin/activate

# Встановити все
pip install --upgrade pip
pip install -r requirements.txt

# Налаштувати .env
nano .env

# Запустити
./startup.sh
```
