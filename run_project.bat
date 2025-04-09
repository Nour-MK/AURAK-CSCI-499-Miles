@echo off
REM Check if the virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    echo Installing dependencies...
    call venv\Scripts\activate
    pip install -r requirements.txt
    deactivate
)

REM Activate the virtual environment
call venv\Scripts\activate

REM Start the FastAPI server minimized
start /min cmd /c "uvicorn main:app --reload"

REM Open the index.html file in the default browser
start index.html