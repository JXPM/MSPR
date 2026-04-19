@echo off
setlocal enabledelayedexpansion

:: ============================================================
::  ObRail Europe - Planificateur de taches Windows
::  Installe la tache mensuelle automatique du pipeline ETL
::  DOIT ETRE EXECUTE EN TANT QU'ADMINISTRATEUR (une seule fois)
:: ============================================================

:: --- CONFIGURATION ---
set TASK_NAME=ObRail_ETL_Mensuel
set ETL_SCRIPT=\MSPR\talend\lancement\lancement.bat
set LOG_DIR=\MSPR\talend\logs
:: ---------------------

echo.
echo ============================================================
echo  ObRail Europe - Installation de la tache planifiee
echo ============================================================
echo.

:: Verifier les droits administrateur
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Ce script doit etre execute en tant qu'Administrateur.
    echo [ERREUR] Clic droit sur le fichier ^> "Executer en tant qu'administrateur"
    pause
    exit /b 1
)

echo [INFO] Droits administrateur confirmes.

:: Verifier que lancement.bat existe
if not exist "%ETL_SCRIPT%" (
    echo [ERREUR] Fichier introuvable : %ETL_SCRIPT%
    echo [ERREUR] Verifiez le chemin dans la section CONFIGURATION de ce script.
    pause
    exit /b 1
)

echo [INFO] Script ETL trouve : %ETL_SCRIPT%

:: Creer le dossier de logs s'il n'existe pas
if not exist "%LOG_DIR%" (
    mkdir "%LOG_DIR%"
    echo [INFO] Dossier de logs cree : %LOG_DIR%
)

:: Supprimer l'ancienne tache si elle existe (mise a jour)
schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Ancienne tache trouvee. Suppression en cours...
    schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1
    echo [INFO] Ancienne tache supprimee.
)

:: Creer la nouvelle tache planifiee
echo [INFO] Creation de la tache planifiee...

schtasks /create ^
    /tn "%TASK_NAME%" ^
    /tr "%ETL_SCRIPT%" ^
    /sc MONTHLY ^
    /d 1 ^
    /st 02:00 ^
    /ru SYSTEM ^
    /rl HIGHEST ^
    /f >nul 2>&1

if %errorlevel% neq 0 (
    echo [ERREUR] Echec de la creation de la tache planifiee.
    echo [ERREUR] Verifiez les droits et la configuration.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  INSTALLATION REUSSIE
echo ============================================================
echo.
echo  Nom de la tache  : %TASK_NAME%
echo  Script execute   : %ETL_SCRIPT%
echo  Planification    : Le 1er de chaque mois a 02h00
echo  Compte           : SYSTEM (sans utilisateur connecte)
echo  Priorite         : HIGHEST
echo.
echo  Pour verifier la tache :
echo    - Ouvrir le Planificateur de taches (taskschd.msc)
echo    - Ou lancer : schtasks /query /tn "%TASK_NAME%" /v
echo.
echo  Pour supprimer la tache :
echo    schtasks /delete /tn "%TASK_NAME%" /f
echo.
echo ============================================================

pause
exit /b 0