# 🚀 Azure Continuous Deployment Setup

Цей проект налаштований для автоматичного розгортання на Azure App Service через GitHub Actions.

## 📁 Структура файлів для розгортання

```
├── .github/workflows/
│   ├── azure-deploy.yml          # Автоматичне розгортання при push
│   └── azure-deploy-manual.yml   # Ручне розгортання
├── db-flask-main/
│   ├── .deployment               # Azure deployment config
│   ├── web.config               # IIS config (Windows)
│   ├── startup.sh               # Linux startup script
│   └── azure-config.md          # Azure configuration guide
├── scripts/
│   ├── deploy-azure.sh          # Azure deployment script
│   └── configure-azure.sh       # Azure configuration script
└── AZURE_DEPLOYMENT_GUIDE.md    # Повна інструкція
```

## ⚡ Швидкий старт

### 1. Створіть Azure App Service
```bash
# Встановіть змінні
export AZURE_WEBAPP_NAME="your-app-name"
export AZURE_RESOURCE_GROUP="your-resource-group"

# Запустіть скрипт
./scripts/deploy-azure.sh
```

### 2. Налаштуйте змінні середовища
```bash
# Встановіть змінні бази даних
export DB_HOST="your-mysql-server.mysql.database.azure.com"
export DB_USER="your-username"
export DB_PASSWORD="your-password"
export DB_NAME="your-database-name"
export SECRET_KEY="your-secret-key"

# Запустіть конфігурацію
./scripts/configure-azure.sh
```

### 3. Налаштуйте GitHub Secrets
1. Отримайте Publish Profile з Azure Portal
2. Додайте secret `AZUREAPPSERVICE_PUBLISHPROFILE_XXX` в GitHub
3. Оновіть назву додатку в `.github/workflows/azure-deploy.yml`

### 4. Зробіть push в main гілку
```bash
git add .
git commit -m "Setup Azure deployment"
git push origin main
```

## 🔧 Налаштування

### Змінні середовища в Azure Portal:
- `DB_HOST` - хост бази даних
- `DB_USER` - користувач бази даних  
- `DB_PASSWORD` - пароль бази даних
- `DB_NAME` - назва бази даних
- `SECRET_KEY` - секретний ключ Flask
- `FLASK_APP=app.py`
- `FLASK_ENV=production`

### GitHub Secrets:
- `AZUREAPPSERVICE_PUBLISHPROFILE_XXX` - Publish Profile з Azure

## 📊 Моніторинг

- **Health Check**: `https://your-app.azurewebsites.net/healthz`
- **API Docs**: `https://your-app.azurewebsites.net/apidocs`
- **Logs**: Azure Portal → App Service → Log stream

## 🛠️ Корисні команди

```bash
# Переглянути логи
az webapp log tail --name your-app-name --resource-group your-resource-group

# Перезапустити додаток
az webapp restart --name your-app-name --resource-group your-resource-group

# Оновити налаштування
az webapp config appsettings set --name your-app-name --resource-group your-resource-group --settings KEY=VALUE
```

## 📚 Детальна інструкція

Дивіться [AZURE_DEPLOYMENT_GUIDE.md](AZURE_DEPLOYMENT_GUIDE.md) для повної інструкції з налаштування.

---

**Примітка**: Замініть `your-app-name`, `your-resource-group` та інші placeholder значення на реальні для вашого проекту.
