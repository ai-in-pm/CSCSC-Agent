@echo off
echo ===== CrewAI Installation Helper =====
echo.
echo This script helps install CrewAI with appropriate options for your environment.
echo.

echo Installation options:
echo 1. Full installation (requires Microsoft C++ Build Tools)
echo 2. Lightweight installation (without chromadb/hnswlib)
echo 3. Exit
echo.

:menu
set /p choice=Enter your choice (1-3): 

if "%choice%"=="1" goto full_install
if "%choice%"=="2" goto light_install
if "%choice%"=="3" goto end

echo Invalid choice. Please try again.
goto menu

:full_install
echo.
echo Checking for virtual environment...

if exist venv\Scripts\activate.bat (
    echo Virtual environment found.
) else (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing Microsoft Visual C++ Build Tools is required.
echo Please download and install from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
echo.
echo After installing the build tools, press any key to continue with CrewAI installation...
pause >nul

echo.
echo Installing CrewAI with full dependencies...
pip install crewai

echo.
echo Installation complete!
echo.
echo Press any key to return to the menu...
pause >nul
goto menu

:light_install
echo.
echo Checking for virtual environment...

if exist venv\Scripts\activate.bat (
    echo Virtual environment found.
) else (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing CrewAI without chromadb (to avoid C++ build tools requirement)...

pip install langchain langchain-openai openai
pip install crewai --no-deps
pip install pydantic==1.10.8 lxml==4.9.3 docx2txt==0.8 typer==0.9.0 pydantic-settings==2.0.3 tavily-python==0.3.1
pip install duckduckgo-search==4.1.0 tenacity==8.2.3 aiohttp unstructured unstructured-client

echo.
echo Installation complete with alternative vector store settings!
echo Note: Some functionality related to document retrieval may be limited.
echo Make sure to set OPENAI_API_KEY in your environment variables.
echo.
echo Press any key to return to the menu...
pause >nul
goto menu

:end
echo.
echo Goodbye!
