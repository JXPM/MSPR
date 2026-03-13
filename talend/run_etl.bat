@echo off
setlocal enabledelayedexpansion

:: ============================================================
::  ObRail Europe - Pipeline ETL Talend
::  Lancement automatique des 9 jobs dans l'ordre
:: ============================================================

:: --- CONFIGURATION ---
set BASE_DIR=C:\Users\josep\Mspr2\MSPR\talend\Jobs
set LOG_DIR=C:\Users\josep\Mspr2\MSPR\talend\logs
:: ---------------------

:: Creer le dossier de logs s'il n'existe pas
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: Nom du fichier de log avec la date du jour
for /f "tokens=1-3 delims=/" %%a in ("%date%") do set TODAY=%%c-%%b-%%a
set LOGFILE=%LOG_DIR%\etl_%TODAY%.log

echo. >> "%LOGFILE%"
echo ============================================================ >> "%LOGFILE%"
echo  DEBUT PIPELINE ETL ObRail - %date% %time% >> "%LOGFILE%"
echo ============================================================ >> "%LOGFILE%"

echo.
echo [INFO] Demarrage du pipeline ETL ObRail...
echo [INFO] Logs enregistres dans : %LOGFILE%
echo.

:: ============================================================
::  EXECUTION DES 9 JOBS DANS L'ORDRE
:: ============================================================

call :run_job "pays"       "%BASE_DIR%\pays\pays_run.bat"
call :run_job "gare"       "%BASE_DIR%\gare\gare_run.bat"
call :run_job "operateur"  "%BASE_DIR%\operateur\operateur_run.bat"
call :run_job "type_train" "%BASE_DIR%\type_train\type_train_run.bat"
call :run_job "ligne"      "%BASE_DIR%\ligne\ligne_run.bat"
call :run_job "trajet"     "%BASE_DIR%\trajet\trajet_run.bat"
call :run_job "exploite"   "%BASE_DIR%\exploite\exploite_run.bat"
call :run_job "itineraire" "%BASE_DIR%\itineraire\itineraire_run.bat"
call :run_job "emission"   "%BASE_DIR%\emission\emission_run.bat"

:: ============================================================
::  FIN DU PIPELINE
:: ============================================================

echo. >> "%LOGFILE%"
echo ============================================================ >> "%LOGFILE%"
echo  PIPELINE TERMINE AVEC SUCCES - %date% %time% >> "%LOGFILE%"
echo ============================================================ >> "%LOGFILE%"

echo.
echo [OK] Pipeline ETL termine avec succes !
echo [OK] Consultez les logs : %LOGFILE%
exit /b 0


:: ============================================================
::  FONCTION : lancer un job et verifier s'il a reussi
:: ============================================================
:run_job
set JOB_NAME=%~1
set JOB_SCRIPT=%~2

echo ------------------------------------------------------ >> "%LOGFILE%"
echo  Job : %JOB_NAME% - Debut : %time% >> "%LOGFILE%"
echo [INFO] Lancement de %JOB_NAME%...

if not exist "%JOB_SCRIPT%" (
    echo [ERREUR] Fichier introuvable : %JOB_SCRIPT% >> "%LOGFILE%"
    echo [ERREUR] Fichier introuvable : %JOB_SCRIPT%
    echo [ERREUR] Pipeline arrete.
    exit /b 1
)

call "%JOB_SCRIPT%" >> "%LOGFILE%" 2>&1
set EXIT_CODE=%errorlevel%

if %EXIT_CODE% neq 0 (
    echo  Job %JOB_NAME% ECHEC - code %EXIT_CODE% - %time% >> "%LOGFILE%"
    echo [ERREUR] %JOB_NAME% a echoue ^(code %EXIT_CODE%^)
    echo [ERREUR] Pipeline arrete. Consultez : %LOGFILE%
    exit /b %EXIT_CODE%
)

echo  Job %JOB_NAME% OK - Fin : %time% >> "%LOGFILE%"
echo [OK] %JOB_NAME% termine.
exit /b 0
