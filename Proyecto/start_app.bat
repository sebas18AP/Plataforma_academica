@echo off
setlocal

REM Cambia al directorio del script
cd /d "%~dp0"

REM Crear entorno virtual si no existe
if not exist ".venv\Scripts\python.exe" (
    echo Creando entorno virtual...
    py -m venv .venv
    if errorlevel 1 (
        echo Error: no se pudo crear el entorno virtual.
        exit /b 1
    )
)

REM Si el entorno existe pero faltan dependencias, instalar.
if exist ".venv\Scripts\python.exe" (
    echo Actualizando pip, setuptools y wheel...
    .venv\Scripts\python -m pip install --upgrade pip setuptools wheel
    if errorlevel 1 (
        echo Error: no se pudo actualizar pip.
        exit /b 1
    )
    echo Instalando dependencias...
    .venv\Scripts\python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: no se pudo instalar las dependencias.
        exit /b 1
    )
)

echo Iniciando la aplicación...
.venv\Scripts\python app.py
endlocal

