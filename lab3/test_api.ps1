# Скрипт для тестування Azure Functions API

Write-Host "=== Тестування Azure Functions API ===" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "https://iot-lab3-functions-fpdsa9hraddjbuck.westeurope-01.azurewebsites.net/api"

# Тест 1: Отримання історії даних
Write-Host "1. Тестування get_sensor_history (останні 10 записів)..." -ForegroundColor Yellow
try {
    $history = Invoke-RestMethod -Uri "$baseUrl/get_sensor_history?limit=10" -Method Get
    Write-Host "   ✓ Успішно! Отримано $($history.Count) записів" -ForegroundColor Green
    if ($history.Count -gt 0) {
        Write-Host "   Приклад запису:" -ForegroundColor Gray
        $history[0] | ConvertTo-Json -Depth 2 | Write-Host -ForegroundColor Gray
    }
} catch {
    Write-Host "   ✗ Помилка: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Тест 2: Історія з фільтром по типу
Write-Host "2. Тестування get_sensor_history з фільтром (temperature)..." -ForegroundColor Yellow
try {
    $tempHistory = Invoke-RestMethod -Uri "$baseUrl/get_sensor_history?sensor_type=temperature&limit=5" -Method Get
    Write-Host "   ✓ Успішно! Отримано $($tempHistory.Count) записів температури" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Помилка: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Тест 3: Статистика за 24 години
Write-Host "3. Тестування get_sensor_stats (останні 24 години)..." -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "$baseUrl/get_sensor_stats" -Method Get
    Write-Host "   ✓ Успішно!" -ForegroundColor Green
    Write-Host "   Період: $($stats.time_period)" -ForegroundColor Gray
    Write-Host "   Загальна статистика:" -ForegroundColor Gray
    Write-Host "     - Всього записів: $($stats.summary.total_readings)" -ForegroundColor Gray
    Write-Host "     - Датчиків: $($stats.summary.total_sensors)" -ForegroundColor Gray
    Write-Host "     - Типів датчиків: $($stats.summary.total_sensor_types)" -ForegroundColor Gray
    
    if ($stats.statistics.Count -gt 0) {
        Write-Host "   Статистика по датчикам:" -ForegroundColor Gray
        foreach ($stat in $stats.statistics) {
            Write-Host "     - $($stat.sensor_id) ($($stat.sensor_type)):" -ForegroundColor Gray
            Write-Host "       Кількість: $($stat.count), Середнє: $($stat.avg_value), Мін: $($stat.min_value), Макс: $($stat.max_value)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "   ✗ Помилка: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Тест 4: Статистика за останній тиждень
Write-Host "4. Тестування get_sensor_stats (останній тиждень)..." -ForegroundColor Yellow
try {
    $weekStats = Invoke-RestMethod -Uri "$baseUrl/get_sensor_stats?time_period=7d" -Method Get
    Write-Host "   ✓ Успішно! Всього записів за тиждень: $($weekStats.summary.total_readings)" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Помилка: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Тест 5: Статистика тільки для temperature
Write-Host "5. Тестування get_sensor_stats з фільтром (temperature)..." -ForegroundColor Yellow
try {
    $tempStats = Invoke-RestMethod -Uri "$baseUrl/get_sensor_stats?sensor_type=temperature&time_period=24h" -Method Get
    Write-Host "   ✓ Успішно!" -ForegroundColor Green
    if ($tempStats.statistics.Count -gt 0) {
        Write-Host "   Датчики температури:" -ForegroundColor Gray
        foreach ($stat in $tempStats.statistics) {
            Write-Host "     $($stat.sensor_id): avg=$($stat.avg_value)°C, min=$($stat.min_value)°C, max=$($stat.max_value)°C" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "   ✗ Помилка: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "=== Тестування завершено ===" -ForegroundColor Cyan

