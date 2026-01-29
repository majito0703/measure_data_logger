@echo off
echo Configurando Git para Measure Data Logger...
echo.

REM Configurar nombre y email de Git
git config --global user.name "Tu Nombre"
git config --global user.email "tuemail@gmail.com"

REM Inicializar repositorio si no existe
if not exist ".git" (
    git init
    git branch -M main
    git remote add origin https://github.com/majito0703/measure_data_logger.git
)

echo.
echo ✅ Configuración completada!
echo.
echo Ahora puedes usar:
echo 1. ejecutar_todo.py - Para todo el proceso
echo 2. auto_git.py - Solo para subir a GitHub
pause
