# Виправлення помилки Azure аутентифікації

## Проблема
```
Error: Login failed with Error: Content is not a valid JSON object. 
Double check if the 'auth-type' is correct.
```

## Причина
Секрет `AZUREAPPSERVICE_CLIENTID_14D15A8C97434B12B01023D5CE8AC6D8` містить невалідний JSON або неправильний формат.

## Рішення

### Варіант 1: Використовувати JSON секрет (рекомендований)

1. **Створіть Service Principal в Azure CLI:**
   ```bash
   az login
   az ad sp create-for-rbac --name "github-actions-deploy" \
     --role contributor \
     --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group-name} \
     --sdk-auth
   ```

2. **Скопіюйте весь JSON вивід та встановіть як секрет:**
   - Назва секрету: `AZURE_CREDENTIALS`
   - Значення: весь JSON вивід (без додаткових символів)

3. **Використовуйте workflow `azure-deploy-json.yml`**

### Варіант 2: Використовувати окремі секрети

Замість одного великого секрету, використовуйте окремі секрети:

1. **Перейдіть до GitHub → Settings → Secrets and variables → Actions**

2. **Видаліть старі секрети:**
   - `AZUREAPPSERVICE_CLIENTID_14D15A8C97434B12B01023D5CE8AC6D8`

3. **Додайте нові секрети:**
   - `AZURE_CLIENT_ID` - Client ID з Service Principal
   - `AZURE_CLIENT_SECRET` - Client Secret з Service Principal  
   - `AZURE_TENANT_ID` - Tenant ID з Azure
   - `AZURE_SUBSCRIPTION_ID` - Subscription ID з Azure

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

## Швидке рішення (JSON секрет)

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

3. **Скопіюйте ВЕСЬ JSON вивід** (включаючи фігурні дужки)

4. **Встановіть в GitHub Secrets:**
   - Назва: `AZURE_CREDENTIALS`
   - Значення: весь JSON (приклад нижче)

### Приклад правильного JSON секрету:
```json
{
  "clientId": "12345678-1234-1234-1234-123456789012",
  "clientSecret": "your-client-secret",
  "subscriptionId": "87654321-4321-4321-4321-210987654321",
  "tenantId": "11111111-2222-3333-4444-555555555555",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

## Перевірка

Після встановлення секретів:
1. Перейдіть до GitHub Actions
2. Запустіть відповідний workflow
3. Перевірте логи на етапі "Azure Login"
