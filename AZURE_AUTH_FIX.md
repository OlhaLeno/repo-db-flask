# Виправлення помилки Azure аутентифікації

## Проблема
```
Error: Login failed with Error: Content is not a valid JSON object. 
Double check if the 'auth-type' is correct.
```

## Причина
Секрет `AZUREAPPSERVICE_CLIENTID_14D15A8C97434B12B01023D5CE8AC6D8` містить невалідний JSON або неправильний формат.

## Рішення

### Варіант 1: Використовувати окремі секрети (рекомендований)

Замість одного великого секрету, використовуйте окремі секрети:

1. **Перейдіть до GitHub → Settings → Secrets and variables → Actions**

2. **Видаліть старий секрет:**
   - `AZUREAPPSERVICE_CLIENTID_14D15A8C97434B12B01023D5CE8AC6D8`

3. **Додайте нові секрети:**
   - `AZURE_CLIENT_ID` - Client ID з Service Principal
   - `AZURE_CLIENT_SECRET` - Client Secret з Service Principal  
   - `AZURE_TENANT_ID` - Tenant ID з Azure
   - `AZURE_SUBSCRIPTION_ID` - Subscription ID з Azure

### Варіант 2: Створити новий Service Principal

1. **Увійдіть в Azure CLI:**
   ```bash
   az login
   ```

2. **Створіть Service Principal:**
   ```bash
   az ad sp create-for-rbac --name "github-actions-deploy" \
     --role contributor \
     --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group-name} \
     --sdk-auth
   ```

3. **Скопіюйте вивід JSON та встановіть як секрет:**
   - Назва секрету: `AZURE_CREDENTIALS`
   - Значення: весь JSON вивід

### Варіант 3: Оновити workflow для використання окремих секретів

Оновіть `simple-deploy.yml`:

```yaml
- name: 'Azure Login'
  uses: azure/login@v1
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    client-secret: ${{ secrets.AZURE_CLIENT_SECRET }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
```

## Швидке рішення

1. **Перейдіть до Azure Portal**
2. **Azure Active Directory → App registrations**
3. **Знайдіть ваш Service Principal**
4. **Скопіюйте:**
   - Application (client) ID
   - Directory (tenant) ID
   - Client secret (з Certificates & secrets)

5. **Встановіть в GitHub Secrets:**
   - `AZURE_CLIENT_ID` = Application ID
   - `AZURE_CLIENT_SECRET` = Client Secret
   - `AZURE_TENANT_ID` = Directory ID
   - `AZURE_SUBSCRIPTION_ID` = Subscription ID

## Перевірка

Після встановлення секретів:
1. Перейдіть до GitHub Actions
2. Запустіть "Simple Azure Deploy"
3. Перевірте логи на етапі "Azure Login"
