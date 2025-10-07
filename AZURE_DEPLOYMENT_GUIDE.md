# 🚀 Налаштування Continuous Deployment на Azure через Git

Цей документ містить повну інструкцію з налаштування автоматичного розгортання Flask додатку на Azure App Service через GitHub.

## 📋 Передумови

- Azure підписка
- GitHub репозиторій з вашим кодом
- Azure CLI встановлений локально
- База даних MySQL (Azure Database for MySQL або інша)

## 🔧 Крок 1: Створення Azure App Service

### 1.1 Через Azure Portal

1. Увійдіть в [Azure Portal](https://portal.azure.com)
2. Натисніть "Create a resource"
3. Оберіть "Web App"
4. Заповніть форму:
   - **Subscription**: Ваша підписка
   - **Resource Group**: Створіть нову або оберіть існуючу
   - **Name**: Унікальна назва для вашого додатку
   - **Runtime stack**: Python 3.9
   - **Operating System**: Linux
   - **Region**: Оберіть найближчий регіон
   - **Pricing plan**: F1 (безкоштовний) або інший

### 1.2 Через Azure CLI

```bash
# Встановіть змінні середовища
export AZURE_WEBAPP_NAME="your-app-name"
export AZURE_RESOURCE_GROUP="your-resource-group"
export AZURE_LOCATION="East US"

# Запустіть скрипт розгортання
./scripts/deploy-azure.sh
```

## 🔐 Крок 2: Налаштування змінних середовища

### 2.1 Через Azure Portal

1. Перейдіть до вашого App Service
2. В меню зліва оберіть "Configuration"
3. В розділі "Application settings" додайте:

```
DB_HOST=your-mysql-server.mysql.database.azure.com
DB_USER=your-username
DB_PASSWORD=your-password
DB_NAME=your-database-name
DB_PORT=3306
SECRET_KEY=your-production-secret-key
FLASK_APP=app.py
FLASK_ENV=production
PYTHONPATH=/home/site/wwwroot
```

### 2.2 Через Azure CLI

```bash
# Встановіть змінні середовища
export DB_HOST="your-mysql-server.mysql.database.azure.com"
export DB_USER="your-username"
export DB_PASSWORD="your-password"
export DB_NAME="your-database-name"
export SECRET_KEY="your-production-secret-key"

# Запустіть скрипт конфігурації
./scripts/configure-azure.sh
```

## 🔑 Крок 3: Налаштування GitHub Secrets

### 3.1 Отримання Publish Profile

1. Перейдіть до вашого App Service в Azure Portal
2. Натисніть "Get publish profile"
3. Збережіть файл `.PublishSettings`

### 3.2 Додавання Secret в GitHub

1. Перейдіть до вашого GitHub репозиторію
2. Натисніть "Settings" → "Secrets and variables" → "Actions"
3. Натисніть "New repository secret"
4. Додайте:
   - **Name**: `AZUREAPPSERVICE_PUBLISHPROFILE_XXX`
   - **Value**: Вміст файлу `.PublishSettings`

## 📝 Крок 4: Оновлення GitHub Actions

### 4.1 Оновіть назву додатку

В файлі `.github/workflows/azure-deploy.yml`:

```yaml
env:
  AZURE_WEBAPP_NAME: 'your-actual-app-name'  # Замініть на реальну назву
```

### 4.2 Оновіть Secret Name

В файлі `.github/workflows/azure-deploy.yml`:

```yaml
publish-profile: ${{ secrets.AZUREAPPSERVICE_PUBLISHPROFILE_YOUR_ACTUAL_SECRET_NAME }}
```

## 🗄️ Крок 5: Налаштування бази даних

### 5.1 Azure Database for MySQL

1. Створіть Azure Database for MySQL
2. Налаштуйте firewall rules для Azure services
3. Створіть базу даних та користувача
4. Виконайте SQL скрипти з `setup_database.sql`

### 5.2 Локальна база даних

Якщо використовуєте локальну базу даних, переконайтеся що:
- База даних доступна з Azure
- Налаштовані firewall rules
- SSL сертифікати налаштовані правильно

## 🚀 Крок 6: Тестування розгортання

### 6.1 Автоматичне розгортання

1. Зробіть commit та push в `main` або `master` гілку
2. Перевірте GitHub Actions вкладку
3. Після успішного розгортання перейдіть на `https://your-app-name.azurewebsites.net`

### 6.2 Ручне розгортання

1. Перейдіть до GitHub Actions
2. Оберіть "Deploy to Azure App Service (Manual)"
3. Натисніть "Run workflow"
4. Оберіть environment та запустіть

## 🔍 Крок 7: Моніторинг та логування

### 7.1 Перегляд логів

1. В Azure Portal перейдіть до App Service
2. Оберіть "Log stream" для real-time логів
3. Або "Logs" для історичних логів

### 7.2 Health Check

Ваш додаток має endpoint `/healthz` для перевірки стану:

```bash
curl https://your-app-name.azurewebsites.net/healthz
```

## 🛠️ Крок 8: Додаткові налаштування

### 8.1 Custom Domain

1. В App Service оберіть "Custom domains"
2. Додайте ваш домен
3. Налаштуйте DNS записи

### 8.2 SSL Certificate

1. В App Service оберіть "TLS/SSL settings"
2. Включіть "HTTPS Only"
3. Налаштуйте SSL сертифікат

### 8.3 Scaling

1. В App Service оберіть "Scale out"
2. Налаштуйте auto-scaling rules
3. Оберіть відповідний pricing tier

## 🚨 Усунення проблем

### Проблема: Deployment failed

**Рішення:**
1. Перевірте логи в GitHub Actions
2. Перевірте Azure App Service logs
3. Переконайтеся що всі змінні середовища встановлені

### Проблема: Database connection error

**Рішення:**
1. Перевірте connection string
2. Переконайтеся що база даних доступна з Azure
3. Перевірте firewall rules

### Проблема: App not starting

**Рішення:**
1. Перевірте `startup.sh` скрипт
2. Переконайтеся що всі залежності встановлені
3. Перевірте Python version

## 📚 Корисні команди

```bash
# Перевірити статус App Service
az webapp show --name your-app-name --resource-group your-resource-group

# Переглянути логи
az webapp log tail --name your-app-name --resource-group your-resource-group

# Перезапустити App Service
az webapp restart --name your-app-name --resource-group your-resource-group

# Оновити app settings
az webapp config appsettings set --name your-app-name --resource-group your-resource-group --settings KEY=VALUE
```

## ✅ Чек-лист для розгортання

- [ ] Azure App Service створено
- [ ] Змінні середовища налаштовані
- [ ] GitHub Secrets додані
- [ ] База даних налаштована
- [ ] GitHub Actions workflow оновлено
- [ ] Тестове розгортання виконано
- [ ] Health check працює
- [ ] Логування налаштовано

---

**Примітка**: Замініть всі placeholder значення (`your-app-name`, `your-resource-group`, тощо) на реальні значення для вашого проекту.
