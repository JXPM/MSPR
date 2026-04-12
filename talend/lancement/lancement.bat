@echo off
setlocal enabledelayedexpansion

:: ============================================================
::  ObRail Europe - Pipeline ETL Talend
:: ============================================================

:: --- CONFIGURATION ---
set BASE_DIR=C:\Users\josep\Mspr2\MSPR\talend\Jobs\Jobs
set LOG_DIR=C:\Users\josep\Mspr2\MSPR\talend\logs
set DUMP_DIR=C:\Users\josep\Mspr2\MSPR\talend\dump
set PGSQL="C:\Program Files\PostgreSQL\18\bin\psql.exe"
set PGDUMP="C:\Program Files\PostgreSQL\18\bin\pg_dump.exe"
set DB_NAME=mspr2
set DB_USER=postgres
:: ---------------------

:: ============================================================
::  SAISIE DU MOT DE PASSE (masque)
:: ============================================================
echo.
for /f "delims=" %%P in ('powershell -Command "$s=Read-Host ''Mot de passe PostgreSQL'' -AsSecureString; [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($s))"') do set PGPASSWORD=%%P
echo.

:: Test de connexion
%PGSQL% -U %DB_USER% -d %DB_NAME% -c "SELECT 1;" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Mot de passe incorrect ou service PostgreSQL inaccessible.
    pause
    exit /b 1
)
echo [OK] Connexion PostgreSQL etablie.
echo.

:: ============================================================
::  PREPARATION
:: ============================================================
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%DUMP_DIR%" mkdir "%DUMP_DIR%"

for /f "tokens=1-3 delims=/" %%a in ("%date%") do set TODAY=%%c-%%b-%%a
set LOGFILE=%LOG_DIR%\lancement_%TODAY%.log

echo ============================================================
echo  ObRail - Lancement complet - %date% %time%
echo ============================================================
echo.
echo ============================================================ >> "%LOGFILE%"
echo  DEBUT - %date% %time% >> "%LOGFILE%"
echo ============================================================ >> "%LOGFILE%"

:: ============================================================
::  ETAPE 1/4 : Correction encodage UTF-8
:: ============================================================
echo [ETAPE 1/4] Correction de l'encodage UTF-8...
echo [ETAPE 1/4] Correction encodage - %time% >> "%LOGFILE%"

for %%J in (pays gare operateur type_train ligne trajet exploite itineraire emission) do (
    set FILE=!BASE_DIR!\%%J\%%J_run.bat
    if exist "!FILE!" (
        copy "!FILE!" "!FILE!.backup" >nul
        powershell -Command "(Get-Content '!FILE!') -replace 'java ', 'java -Dfile.encoding=UTF-8 ' | Set-Content '!FILE!'"
        echo   [OK] %%J modifie >> "%LOGFILE%"
    ) else (
        echo   [ERREUR] Introuvable : !FILE! >> "%LOGFILE%"
    )
)
echo [OK] Encodage corrige.
echo.

:: ============================================================
::  ETAPE 2/4 : Nettoyage de la base
:: ============================================================
echo [ETAPE 2/4] Nettoyage de la base de donnees...
echo [ETAPE 2/4] Nettoyage - %time% >> "%LOGFILE%"

%PGSQL% -U %DB_USER% -d %DB_NAME% -c "SET session_replication_role = 'replica';" >> "%LOGFILE%" 2>&1

for %%T in (emission itineraire exploite trajet ligne type_train operateur gare pays) do (
    echo   Nettoyage %%T... >> "%LOGFILE%"
    %PGSQL% -U %DB_USER% -d %DB_NAME% -c "TRUNCATE TABLE %%T CASCADE;" >> "%LOGFILE%" 2>&1
)

%PGSQL% -U %DB_USER% -d %DB_NAME% -c "SET session_replication_role = 'origin';" >> "%LOGFILE%" 2>&1
echo [OK] Nettoyage termine.
echo.

:: ============================================================
::  ETAPE 3/4 : Jobs ETL
:: ============================================================
echo [ETAPE 3/4] Lancement des jobs ETL...
echo [ETAPE 3/4] Jobs ETL - %time% >> "%LOGFILE%"

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
::  ETAPE 4/4 : Dump PostgreSQL
:: ============================================================
echo [ETAPE 4/4] Generation du dump...
echo [ETAPE 4/4] Dump - %time% >> "%LOGFILE%"

set DUMPFILE=%DUMP_DIR%\mspr2_dump_%TODAY%.sql
%PGDUMP% -U %DB_USER% -d %DB_NAME% --no-password -F p -f "%DUMPFILE%" >> "%LOGFILE%" 2>&1

if %errorlevel% neq 0 (
    echo [ERREUR] Dump echoue. Consultez : %LOGFILE%
) else (
    echo [OK] Dump genere : %DUMPFILE%
)

set PGPASSWORD=

:: ============================================================
::  FIN
:: ============================================================
echo.
echo ============================================================
echo  TERMINE ! Log : %LOGFILE%
echo ============================================================
echo.
pause
exit /b 0


:: ============================================================
::  FONCTION : run_job
:: ============================================================
:run_job
set JOB_NAME=%~1
set JOB_SCRIPT=%~2

echo [INFO] Lancement de %JOB_NAME%...
echo  Job %JOB_NAME% - Debut : %time% >> "%LOGFILE%"

if not exist "%JOB_SCRIPT%" (
    echo [ERREUR] Introuvable : %JOB_SCRIPT%
    echo [ERREUR] Introuvable : %JOB_SCRIPT% >> "%LOGFILE%"
    pause
    exit /b 1
)

call "%JOB_SCRIPT%" >> "%LOGFILE%" 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] %JOB_NAME% a echoue. Consultez : %LOGFILE%
    echo  Job %JOB_NAME% ECHEC - %time% >> "%LOGFILE%"
    pause
    exit /b 1
)

echo [OK] %JOB_NAME% termine.
echo  Job %JOB_NAME% OK - Fin : %time% >> "%LOGFILE%"
exit /b 0