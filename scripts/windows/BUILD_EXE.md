# Сборка Langflow.exe (Windows)

Скрипты в этой папке упаковывают Langflow в один исполняемый файл через [PyInstaller](https://pyinstaller.org/).

> **Важно:** это неофициальная сборка из исходников OSS. Готовый установщик с автообновлением — [Langflow Desktop](https://www.langflow.org/desktop).

## Требования

| Инструмент | Версия |
|------------|--------|
| Python | 3.13 (рекомендуется для сборки; в репозитории есть `.python-version`). 3.14 возможен, но на Windows часто нужны [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) |
| [uv](https://docs.astral.sh/uv/) | любая актуальная |
| Node.js + **npm** | LTS с [nodejs.org](https://nodejs.org/) |
| Диск | ~5–10 GB свободно (кэш + сборка) |
| RAM | 8 GB+ рекомендуется |

## Быстрый старт

Из корня репозитория (`langflow-main`):

```powershell
.\scripts\windows\build_exe.ps1
```

Или двойной клик по `build_exe.bat`.

Результат: `dist\Langflow.exe`

## Запуск

**Рекомендуется** — `dist\Langflow.bat` (окно консоли остаётся открытым, виден весь вывод):

```powershell
.\dist\Langflow.bat
```

Или из cmd:

```powershell
.\dist\Langflow.exe run
```

Откройте http://127.0.0.1:7860 в браузере (Chrome/Edge). Сам exe — это сервер, не окно с интерфейсом.

Лог при проблемах: `%USERPROFILE%\.langflow\langflow-exe.log`

Данные и настройки сохраняются в `%USERPROFILE%\.langflow`.

## Только фронтенд (без exe)

```powershell
.\scripts\windows\build_frontend_only.ps1
uv run langflow run
```

## Файлы

| Файл | Назначение |
|------|------------|
| `build_exe.ps1` | Полный пайплайн: npm → frontend → PyInstaller |
| `langflow.spec` | Конфигурация PyInstaller |
| `langflow_frozen_entry.py` | Точка входа для frozen-сборки |
| `langflow/utils/frozen_bundle.py` | Пути к UI внутри `_MEIPASS` |

## Ограничения

- Первая сборка долгая (зависимости + анализ PyInstaller).
- Размер exe часто **1–3+ GB** из-за ML/NLP-зависимостей.
- Не все опциональные интеграции (Docling, CUDA и т.д.) могут работать без доработки spec.
- Антивирусы иногда блокируют PyInstaller-бинарники — добавьте исключение при необходимости.

## Устранение неполадок

**`No module named 'passlib.handlers.bcrypt'`** — пересоберите exe после обновления `langflow.spec` (добавлен hook для passlib):

```powershell
.\scripts\windows\build_exe.ps1
```

**Нет вывода в окне exe** — не запускайте exe двойным кликом из проводника (окно может мгновенно закрыться). Используйте **`dist\Langflow.bat`** или cmd: `Langflow.exe run`. Смотрите лог `%USERPROFILE%\.langflow\langflow-exe.log`.

**Пустой экран в браузере** — дождитесь в консоли строки с `http://127.0.0.1:7860`, затем откройте этот адрес вручную.

**`PermissionError` / `WinError 5` на `dist\Langflow.exe`** — exe запущен или заблокирован антивирусом. Закройте Langflow.bat/exe, в диспетчере задач завершите `Langflow.exe`, затем снова `build_exe.ps1` (скрипт сам пытается остановить процесс).

**`npm` не найден** — установите Node.js LTS и перезапустите терминал.

**`Frontend build not found`** — сначала выполните `build_frontend_only.ps1`.

**Сборка падает по памяти** — закройте лишние приложения или используйте `uv sync` без лишних extras.

**Официальный Desktop** — если нужен стабильный установщик с обновлениями, используйте https://www.langflow.org/desktop .
