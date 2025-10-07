# 🚀 Налаштування Continuous Deployment на Azure VM

Оскільки у вас вже є віртуальна машина на Azure з базою даних, я налаштував систему для автоматичного розгортання через GitHub Actions на вашу VM.

## 📁 Створені файли для VM deployment:

### ✅ GitHub Actions Workflow
- `.github/workflows/azure-vm-deploy.yml` - автоматичне розгортання на VM при push

### ✅ Deployment Scripts
- `scripts/setup-vm.sh` - налаштування VM для Flask додатку
- `scripts/deploy-to-vm.sh` - розгортання додатку на VM

## 🔧 Крок 1: Налаштування SSH ключів

### 1.1 Створення SSH ключа (якщо немає)
```bash
# Створити SSH ключ
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""

# Показати публічний ключ
cat ~/.ssh/id_rsa.pub
```

### 1.2 Додавання ключа на VM
```bash
# Скопіювати публічний ключ на VM
ssh-copy-id azureuser@your-vm-ip

# Або вручну
ssh azureuser@your-vm-ip
mkdir -p ~/.ssh
echo "your-public-key-content" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

## 🔑 Крок 2: Налаштування GitHub Secrets

В GitHub репозиторії додайте наступні secrets:

1. **VM_HOST** - IP адреса вашої VM
2. **VM_USERNAME** - ім'я користувача (зазвичай `azureuser`)
3. **VM_SSH_KEY** - приватний SSH ключ (вміст файлу `~/.ssh/id_rsa`)

### Як додати secrets:
1. Перейдіть до GitHub репозиторію
2. Settings → Secrets and variables → Actions
3. New repository secret
4. Додайте кожен secret окремо

## 🛠️ Крок 3: Налаштування VM

### 3.1 Запустіть скрипт налаштування VM
```bash
# Встановіть змінні
export VM_HOST="your-vm-ip"
export VM_USERNAME="azureuser"

# Запустіть налаштування
./scripts/setup-vm.sh
```

Цей скрипт встановить:
- Python 3.9 та pip
- nginx (reverse proxy)
- systemd service для вашого додатку
- Налаштує автоматичний запуск

### 3.2 Налаштування змінних середовища на VM
```bash
# Підключіться до VM
ssh azureuser@your-vm-ip

# Створіть файл з змінними середовища
nano /home/azureuser/bus-management-api/.env
```

Додайте в `.env` файл:
```
DB_HOST=your-database-host
DB_USER=your-database-user
DB_PASSWORD=your-database-password
DB_NAME=your-database-name
DB_PORT=3306
SECRET_KEY=your-production-secret-key
FLASK_APP=app.py
FLASK_ENV=production
```

## 🚀 Крок 4: Тестування розгортання

### 4.1 Ручне розгортання
```bash
# Встановіть змінні
export VM_HOST="your-vm-ip"
export VM_USERNAME="azureuser"

# Запустіть розгортання
./scripts/deploy-to-vm.sh
```

### 4.2 Автоматичне розгортання
1. Зробіть commit та push в main гілку
2. GitHub Actions автоматично розгорне додаток на VM
3. Перевірте логи в GitHub Actions вкладці

## 🔍 Крок 5: Перевірка роботи

### 5.1 Health Check
```bash
curl http://your-vm-ip/healthz
```

### 5.2 API Documentation
```bash
curl http://your-vm-ip/apidocs
```

### 5.3 Перевірка сервісу на VM
```bash
ssh azureuser@your-vm-ip
sudo systemctl status bus-management-api
sudo journalctl -u bus-management-api -f
```

## 🌐 Крок 6: Налаштування домену (опціонально)

### 6.1 Налаштування DNS
- Налаштуйте A-запис вашого домену на IP адресу VM

### 6.2 SSL сертифікат
```bash
# Встановіть certbot
sudo apt install certbot python3-certbot-nginx

# Отримайте SSL сертифікат
sudo certbot --nginx -d your-domain.com
```

## 🛠️ Корисні команди

```bash
# Перезапустити сервіс
sudo systemctl restart bus-management-api

# Переглянути логи
sudo journalctl -u bus-management-api -f

# Перевірити статус nginx
sudo systemctl status nginx

# Перезавантажити nginx
sudo systemctl reload nginx

# Переглянути процеси
ps aux | grep gunicorn
```

## ⚠️ Важливі зауваження

1. **Firewall**: Переконайтеся що порт 80 відкритий в Azure VM
2. **SSH безпека**: Використовуйте SSH ключі замість паролів
3. **Backup**: Регулярно робіть backup бази даних
4. **Monitoring**: Налаштуйте моніторинг для VM та додатку

## 🎯 Результат

Після налаштування:
- ✅ Автоматичне розгортання при push в main гілку
- ✅ Health check endpoint: `http://your-vm-ip/healthz`
- ✅ API документація: `http://your-vm-ip/apidocs`
- ✅ Автоматичний перезапуск при збоях
- ✅ Reverse proxy через nginx
- ✅ Логування через systemd

Ваш Flask додаток тепер буде автоматично розгортатися на Azure VM при кожному push! 🎉
