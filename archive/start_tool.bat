@echo off
echo Startar NewPipe Metadata Tool...
echo.
python newpipe_metadata_tool.py
if %errorlevel% neq 0 (
    echo.
    echo Fel: Python hittades inte eller appen kraschade.
    echo Kontrollera att Python ar installerat.
    pause
)
