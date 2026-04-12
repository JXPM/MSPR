@echo off
setlocal enabledelayedexpansion

:: ============================================================
::  ObRail Europe - Pipeline ETL Talend
::  Lancement complet : correction encodage + 9 jobs ETL
:: ============================================================

:: --- CONFIGURATION ---
set BASE_DIR=C:\Users\josep\Mspr2\MSPR\talend\Jobs\Jobs
set LOG_DIR=C:\Users\josep\Mspr2\MSPR\talend\logs
set DUMP_DIR=C:\Users\josep\Mspr2\MSPR\talend\dump
set PGSQL="C:\Program Files\PostgreSQL\18\bin\psql.exe"
set PGDUMP="C:\Program Files\PostgreSQL\18\bin\pg_dump.exe"
set DB_NAME=mspr2
set DB_USER=postgres
set DB_PASSWORD="password"
:: ---------------------

:: Creer les dossiers necessaires s'ils n'existent pas
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%DUMP_DIR%" mkdir "%DUMP_DIR%"

:: Nom du fichier de log avec la date du jour
for /f "tokens=1-3 delims=/" %%a in ("%date%") do set TODAY=%%c-%%b-%%a
set LOGFILE=%LOG_DIR%\lancement_%TODAY%.log

echo.
echo ============================================================
echo  ObRail - Lancement complet - %date% %time%
echo ============================================================
echo.
echo ============================================================ >> "%LOGFILE%"
echo  DEBUT LANCEMENT COMPLET - %date% %time% >> "%LOGFILE%"
echo ============================================================ >> "%LOGFILE%"

:: ============================================================
::  ETAPE 1 : Correction de l'encodage UTF-8
:: ============================================================
echo [ETAPE 1/3] Correction de l'encodage UTF-8...
echo [ETAPE 1/3] Correction encodage - %time% >> "%LOGFILE%"

for %%J in (pays gare operateur type_train ligne trajet exploite itineraire emission) do (
    set FILE=!BASE_DIR!\%%J\%%J_run.bat

    if exist "!FILE!" (
        echo   Modification de %%J_run.bat...
        copy "!FILE!" "!FILE!.backup" >nul
        powershell -Command "(Get-Content '!FILE!') -replace 'java ', 'java -Dfile.encoding=UTF-8 ' | Set-Content '!FILE!'"
        echo   [OK] %%J_run.bat modifie >> "%LOGFILE%"
    ) else (
        echo   [ERREUR] Fichier introuvable : !FILE!
        echo   [ERREUR] Fichier introuvable : !FILE! >> "%LOGFILE%"
    )
)

echo [OK] Correction encodage terminee.
echo [OK] Correction encodage terminee - %time% >> "%LOGFILE%"
echo.

:: ============================================================
::  ETAPE 2 : Nettoyage de la base de donnees
:: ============================================================
echo [ETAPE 2/3] Nettoyage de la base de donnees...
echo. >> "%LOGFILE%"
echo [ETAPE 2/3] Nettoyage base - %time% >> "%LOGFILE%"

set PGPASSWORD=%DB_PASSWORD%
set PGPASSWORD=%PGPASSWORD:"=%

%PGSQL% -U %DB_USER% -d %DB_NAME% -c "SET session_replication_role = 'replica';" >> "%LOGFILE%" 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Connexion PostgreSQL echouee. Verifiez mot de passe et service.
    echo [ERREUR] Connexion PostgreSQL echouee - %time% >> "%LOGFILE%"
    pause
    exit /b 1
)

for %%T in (emission itineraire exploite trajet ligne type_train operateur gare pays) do (
    echo   Nettoyage de la table %%T... >> "%LOGFILE%"
    %PGSQL% -U %DB_USER% -d %DB_NAME% -c "TRUNCATE TABLE %%T CASCADE;" >> "%LOGFILE%" 2>&1
)

%PGSQL% -U %DB_USER% -d %DB_NAME% -c "SET session_replication_role = 'origin';" >> "%LOGFILE%" 2>&1
set PGPASSWORD=

echo [OK] Nettoyage termine.
echo [OK] Nettoyage termine - %time% >> "%LOGFILE%"
echo.

:: ============================================================
::  ETAPE 3 : Execution des 9 jobs ETL dans l'ordre
:: ============================================================
echo [ETAPE 3/3] Lancement des jobs ETL...
echo. >> "%LOGFILE%"
echo [ETAPE 3/3] Lancement jobs ETL - %time% >> "%LOGFILE%"

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
::  ETAPE 4 : Dump de la base de donnees (snapshot temps reel)
:: ============================================================
echo [ETAPE 4/4] Generation du dump PostgreSQL...
echo. >> "%LOGFILE%"
echo [ETAPE 4/4] Dump base - %time% >> "%LOGFILE%"

set DUMPFILE=%DUMP_DIR%\mspr2_dump_%TODAY%.sql

set PGPASSWORD=%DB_PASSWORD%
set PGPASSWORD=%PGPASSWORD:"=%

%PGDUMP% -U %DB_USER% -d %DB_NAME% --no-password -F p -f "%DUMPFILE%" >> "%LOGFILE%" 2>&1

if %errorlevel% neq 0 (
    echo [ERREUR] Dump PostgreSQL echoue. Consultez : %LOGFILE%
    echo [ERREUR] Dump echoue - %time% >> "%LOGFILE%"
) else (
    echo [OK] Dump genere : %DUMPFILE%
    echo [OK] Dump genere : %DUMPFILE% - %time% >> "%LOGFILE%"
)

set PGPASSWORD=

echo.

:: ============================================================
::  FIN
:: ============================================================
echo.
echo ============================================================
echo  PROCESSUS COMPLET TERMINE AVEC SUCCES !
echo  Log  : %LOGFILE%
echo  Dump : %DUMPFILE%
echo ============================================================
echo.
echo ============================================================ >> "%LOGFILE%"
echo  PROCESSUS COMPLET TERMINE AVEC SUCCES - %date% %time% >> "%LOGFILE%"
echo  Dump : %DUMPFILE% >> "%LOGFILE%"
echo ============================================================ >> "%LOGFILE%"

pause
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
