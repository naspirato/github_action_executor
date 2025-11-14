# Быстрый старт

## 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

## 2. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и заполните:

```bash
cp .env.example .env
```

Минимально необходимые переменные:
- `SECRET_KEY` - любой случайный секретный ключ
- `GITHUB_CLIENT_ID` и `GITHUB_CLIENT_SECRET` - из OAuth App
- `GITHUB_APP_ID` и `GITHUB_APP_INSTALLATION_ID` - из GitHub App
- `GITHUB_APP_PRIVATE_KEY_PATH` - путь к файлу с приватным ключом

## 3. Создание GitHub App Private Key

Скачайте приватный ключ из настроек GitHub App и сохраните как `github-app-private-key.pem`:

```bash
# Файл должен быть в формате:
# -----BEGIN RSA PRIVATE KEY-----
# ...
# -----END RSA PRIVATE KEY-----
```

## 4. Запуск приложения

```bash
python app.py
```

Или с hot-reload:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## 5. Откройте в браузере

http://localhost:8000

## Тестирование

1. Нажмите "Войти через GitHub"
2. Авторизуйтесь
3. Заполните форму с репозиторием и workflow
4. Выберите тесты
5. Запустите workflow

## Пример workflow для тестирования

Создайте файл `.github/workflows/test.yml` в вашем репозитории:

```yaml
name: Test Workflow

on:
  workflow_dispatch:
    inputs:
      tests:
        description: 'Tests to run (comma-separated)'
        required: false
        type: string
        default: 'unit'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Run tests
        run: |
          echo "Running tests: ${{ inputs.tests }}"
          # Ваши команды для запуска тестов
```

## Troubleshooting

### Ошибка "Not authenticated"
- Убедитесь, что вы авторизовались через GitHub OAuth
- Проверьте, что `GITHUB_CLIENT_ID` и `GITHUB_CLIENT_SECRET` правильные

### Ошибка "Failed to trigger workflow"
- Проверьте, что GitHub App установлен в репозиторий
- Убедитесь, что у App есть права на Actions (Read and write)
- Проверьте, что `workflow_id` соответствует имени файла workflow

### Ошибка "User is not a collaborator"
- Убедитесь, что вы действительно коллаборатор репозитория (имеете доступ к репозиторию)
- Проверьте, что OAuth токен имеет права на чтение репозитория

### Ошибка "OAuth App access restrictions"
Если вы видите ошибку:
```
Although you appear to have the correct authorization credentials, 
the `organization-name` organization has enabled OAuth App access restrictions
```

Это означает, что организация включила ограничения доступа для OAuth приложений. Чтобы решить проблему:

1. **Если вы владелец организации или имеете права администратора:**
   - Перейдите в настройки организации: `https://github.com/organizations/ORGANIZATION_NAME/settings/oauth_application_policy`
   - Найдите ваше OAuth App в списке "Third-party access"
   - Нажмите "Grant" или "Approve" для вашего приложения
   - Подробнее: https://docs.github.com/articles/restricting-access-to-your-organization-s-data/

2. **Если вы не администратор организации:**
   - Обратитесь к администратору организации
   - Попросите его одобрить OAuth App в настройках организации
   - Администратор должен перейти в: `Settings → Third-party access → OAuth Apps`
   - И одобрить ваше приложение

3. **Альтернативное решение:**
   - Если у вас нет доступа к настройкам организации, можно использовать GitHub App вместо OAuth App
   - GitHub Apps не требуют одобрения организации (если установлены в репозиторий)

