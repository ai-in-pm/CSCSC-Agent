@echo off
echo ===== AI EVM Agent with Physical AI Capabilities =====
echo.
echo Available commands:
echo 1. Start the API Server
echo 2. Run the Physical AI Demo (all capabilities)
echo 3. Run Environmental Impact Demo
echo 4. Run Supply Chain Impact Demo
echo 5. Run Site Progress Adjustment Demo
echo 6. Run Risk Assessment Demo
echo 7. Run CrewAI Integration Demo
echo 8. Exit
echo.

:menu
set /p choice=Enter your choice (1-8): 

if "%choice%"=="1" goto start_server
if "%choice%"=="2" goto run_all_demos
if "%choice%"=="3" goto run_environmental_demo
if "%choice%"=="4" goto run_supply_chain_demo
if "%choice%"=="5" goto run_site_progress_demo
if "%choice%"=="6" goto run_risk_demo
if "%choice%"=="7" goto run_crewai_demo
if "%choice%"=="8" goto end

echo Invalid choice. Please try again.
goto menu

:start_server
echo.
echo Starting AI EVM Agent API Server...
echo Press Ctrl+C to stop the server when finished.
python -m src.main
goto end

:run_all_demos
echo.
echo Running full Physical AI Demo...
python -m src.demo.physical_ai_demo --type all
echo.
echo Demo complete. Press any key to return to the menu...
pause >nul
goto menu

:run_environmental_demo
echo.
echo Running Environmental Impact Demo...
python -m src.demo.physical_ai_demo --type environmental
echo.
echo Demo complete. Press any key to return to the menu...
pause >nul
goto menu

:run_supply_chain_demo
echo.
echo Running Supply Chain Impact Demo...
python -m src.demo.physical_ai_demo --type supply_chain
echo.
echo Demo complete. Press any key to return to the menu...
pause >nul
goto menu

:run_site_progress_demo
echo.
echo Running Site Progress Adjustment Demo...
python -m src.demo.physical_ai_demo --type site_progress
echo.
echo Demo complete. Press any key to return to the menu...
pause >nul
goto menu

:run_risk_demo
echo.
echo Running Risk Assessment Demo...
python -m src.demo.physical_ai_demo --type risk
echo.
echo Demo complete. Press any key to return to the menu...
pause >nul
goto menu

:run_crewai_demo
echo.
echo Running CrewAI Integration Demo...
echo NOTE: This requires an OpenAI API key set as OPENAI_API_KEY environment variable.
echo.
set /p api_key=Enter your OpenAI API key (or press Enter to use environment variable): 

if "%api_key%"=="" (
    echo Using OpenAI API key from environment variable...
    python -m src.demo.crewai_demo --type all
) else (
    echo Using provided OpenAI API key...
    python -m src.demo.crewai_demo --api-key %api_key% --type all
)

echo.
echo Demo complete. Press any key to return to the menu...
pause >nul
goto menu

:end
echo.
echo Goodbye!
