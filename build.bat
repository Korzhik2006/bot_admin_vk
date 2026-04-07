@echo off
echo Установка зависимостей...
pip install -r requirements.txt

echo Очистка предыдущих сборок...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"

echo Сборка исполняемого файла...
pyinstaller --onefile --windowed --name optica_bot main.py

echo Сборка завершена. Файл optica_bot.exe находится в папке dist\.
pause