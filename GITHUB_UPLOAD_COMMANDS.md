# Загрузка проекта на GitHub

Откройте PowerShell в папке проекта:

```powershell
cd C:\Users\e_vla\Desktop\вцув\ПРОЕКТ
```

Проверьте, что Git установлен:

```powershell
git --version
```

Инициализируйте репозиторий:

```powershell
git init
git branch -M main
```

Проверьте, какие файлы попадут в commit:

```powershell
git status
```

Добавьте файлы:

```powershell
git add .
```

Создайте commit:

```powershell
git commit -m "Add CoworkBooking data platform project"
```

Создайте пустой репозиторий на GitHub, затем подключите remote:

```powershell
git remote add origin https://github.com/USERNAME/REPOSITORY.git
```

Загрузите проект:

```powershell
git push -u origin main
```

После загрузки откройте вкладку **Actions** на GitHub и проверьте workflow `CI`.

Важно:

- `.env` не загружается, потому что он в `.gitignore`.
- `data/runtime` не загружается, потому что это результаты локального запуска.
- `__pycache__`, `node_modules`, `.terraform`, временные файлы и архивы не загружаются.
