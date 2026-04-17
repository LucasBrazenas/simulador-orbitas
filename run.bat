@echo off
setlocal

set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

set "PYTHON_CMD="

if exist "%ROOT_DIR%.venv\Scripts\python.exe" (
    set "PYTHON_CMD="%ROOT_DIR%.venv\Scripts\python.exe""
) else (
    py -3 -c "import sys" >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_CMD=py -3"
    ) else (
        python -c "import sys" >nul 2>&1
        if not errorlevel 1 (
            set "PYTHON_CMD=python"
        )
    )
)

if not defined PYTHON_CMD (
    echo Error: no se encontro un interprete de Python. Instala Python 3 o crea .venv.
    exit /b 1
)

call %PYTHON_CMD% -c "import uvicorn" >nul 2>&1
if errorlevel 1 (
    echo Error: faltan dependencias del backend. Ejecuta %PYTHON_CMD% -m pip install -r requirements.txt
    exit /b 1
)

echo Iniciando backend en http://127.0.0.1:8000 ...
start "Simulador Backend" cmd /k "cd /d \"%ROOT_DIR%\" && %PYTHON_CMD% -m uvicorn backend.server:app --host 127.0.0.1 --port 8000"

echo Iniciando frontend estatico en http://127.0.0.1:5173 ...
start "Simulador Frontend" cmd /k "cd /d \"%ROOT_DIR%\" && %PYTHON_CMD% -m http.server 5173"

echo.
echo Simulador disponible en: http://127.0.0.1:5173/frontend/
echo Se abrieron dos ventanas nuevas: una para el backend y otra para el frontend.
echo Para detener el proyecto, cerra ambas ventanas.

start "" "http://127.0.0.1:5173/frontend/"
