# Основы работы с GitHub для проекта WorkflowV2

Краткая инструкция для ежедневной работы с репозиторием проекта.

**Репозиторий:** https://github.com/kozlovab123-lab/workflowv2  
**Локальная папка:** `C:\ZER\PEl02\workflowv2`  
**Основная ветка:** `master`

---

## 1. Что такое Git и GitHub

- **Git** — система контроля версий на вашем компьютере. Хранит историю изменений файлов.
- **GitHub** — облачный сервис, где лежит копия проекта и с которым можно синхронизировать локальную папку.

Типичный цикл работы:

1. Изменили файлы локально
2. Зафиксировали изменения (**commit**)
3. Отправили на GitHub (**push**)

---

## 2. Первичная настройка (один раз)

### Git

Проверка:

```powershell
git --version
```

Если Git не установлен — скачайте с https://git-scm.com/download/win

### GitHub CLI (рекомендуется)

Удобен для входа в аккаунт и работы с репозиториями:

```powershell
winget install GitHub.cli
gh auth login
```

При входе выберите:

- GitHub.com
- HTTPS
- Вход через браузер

Проверка:

```powershell
gh auth status
```

### Клонирование на другом компьютере

```powershell
git clone https://github.com/kozlovab123-lab/workflowv2.git
cd workflowv2
```

---

## 3. Ежедневная работа

Все команды выполняйте в папке проекта:

```powershell
cd C:\ZER\PEl02\workflowv2
```

### Посмотреть, что изменилось

```powershell
git status
```

Краткий список изменённых файлов:

```powershell
git status --short
```

### Сохранить изменения (commit)

```powershell
git add .
git commit -m "Кратко: что сделано и зачем"
```

Примеры сообщений:

- `fix: доступ к сайту из локальной сети`
- `feat: добавить русскую локализацию`
- `docs: обновить инструкцию по запуску`

### Отправить на GitHub

```powershell
git push
```

Если ветка ещё не привязана к удалённой:

```powershell
git push -u origin master
```

### Забрать изменения с GitHub

Перед началом работы или если проект меняли с другого ПК:

```powershell
git pull
```

---

## 4. Полезные команды

| Задача | Команда |
|--------|---------|
| История коммитов | `git log --oneline -10` |
| Что изменилось в файлах | `git diff` |
| Отменить незакоммиченные правки в файле | `git checkout -- путь\к\файлу` |
| Убрать файл из индекса (перед commit) | `git restore --staged путь\к\файлу` |
| Открыть репозиторий в браузере | `gh repo view --web` |
| Список веток | `git branch -a` |

---

## 5. Что нельзя коммитить

В проекте уже настроен `.gitignore`. **Не добавляйте в Git:**

- `.env` — пароли, API-ключи, настройки БД
- `.venv/` — виртуальное окружение Python
- `node_modules/` — зависимости frontend
- `langflow.db` и другие локальные базы данных
- логи, кэши, временные файлы

Если случайно закоммитили секрет — его нужно удалить из истории; проще сразу не коммитить `.env`.

---

## 6. Ветки (кратко)

Ветка — отдельная линия разработки.

Создать ветку для новой задачи:

```powershell
git checkout -b feature/название-задачи
```

После работы:

```powershell
git add .
git commit -m "feat: описание"
git push -u origin feature/название-задачи
```

На GitHub можно создать **Pull Request** — запрос на слияние ветки в `master`.

Вернуться в основную ветку:

```powershell
git checkout master
git pull
```

---

## 7. Работа через сайт GitHub

На странице репозитория: https://github.com/kozlovab123-lab/workflowv2

- **Code** — просмотр файлов
- **Commits** — история изменений
- **Issues** — задачи и баги
- **Pull requests** — предложения изменений
- **Settings** — настройки репозитория (видимость, доступы)

Кнопка **Upload files** подходит для мелких правок; для регулярной разработки удобнее `git` в терминале.

---

## 8. Типичные проблемы

### `git push` просит логин и пароль

Используйте вход через GitHub CLI:

```powershell
gh auth login
```

Для HTTPS GitHub **не принимает обычный пароль** — нужен токен или авторизация через `gh`.

### `rejected` / `failed to push`

Кто-то уже отправил изменения на GitHub. Сначала подтяните их:

```powershell
git pull
```

Затем снова:

```powershell
git push
```

### Конфликт при `git pull`

Git не смог автоматически объединить изменения. Откройте файлы с маркерами `<<<<<<<`, исправьте вручную, затем:

```powershell
git add .
git commit -m "merge: разрешить конфликт"
git push
```

### Случайно изменили лишние файлы

Посмотреть:

```powershell
git status
```

Отменить изменения в конкретном файле (осторожно — правки пропадут):

```powershell
git restore путь\к\файлу
```

---

## 9. Рекомендуемый порядок перед завершением работы

```powershell
cd C:\ZER\PEl02\workflowv2
git status
git add .
git commit -m "описание изменений"
git push
```

Проверьте на GitHub, что коммит появился в списке **Commits**.

---

## 10. Связь с запуском проекта

Запуск приложения и работа с Git — разные вещи:

- **Запуск:** `LangflowV2-Start.bat` или `make run_cli`
- **Сохранение кода:** `git add` → `git commit` → `git push`

После `git pull` на другом компьютере может понадобиться обновить зависимости:

```powershell
uv sync
cd src\frontend
npm install
```

---

## Полезные ссылки

- Профиль: https://github.com/kozlovab123-lab
- Репозиторий проекта: https://github.com/kozlovab123-lab/workflowv2
- Документация Git: https://git-scm.com/doc
- Документация GitHub: https://docs.github.com/ru
