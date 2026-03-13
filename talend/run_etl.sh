#!/bin/bash
# ============================================================
#  ObRail Europe - Pipeline ETL Talend (Linux)
#  Equivalent de run_etl.bat pour serveur Ubuntu/Debian
#  Lancement automatique des 9 jobs dans l'ordre
# ============================================================

# --- CONFIGURATION ---
BASE_DIR="/opt/obRail/talend/Jobs"
LOG_DIR="/var/log/obRail"
# ---------------------

# Creer le dossier de logs s'il n'existe pas
mkdir -p "$LOG_DIR"

# Nom du fichier de log avec la date du jour
TODAY=$(date +%Y-%m-%d)
LOGFILE="$LOG_DIR/etl_${TODAY}.log"

echo "" >> "$LOGFILE"
echo "============================================================" >> "$LOGFILE"
echo " DEBUT PIPELINE ETL ObRail - $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOGFILE"
echo "============================================================" >> "$LOGFILE"

echo ""
echo "[INFO] Demarrage du pipeline ETL ObRail..."
echo "[INFO] Logs enregistres dans : $LOGFILE"
echo ""

# ============================================================
#  FONCTION : lancer un job et verifier s'il a reussi
# ============================================================
run_job() {
    local JOB_NAME="$1"
    local JOB_SCRIPT="$2"

    echo "------------------------------------------------------" >> "$LOGFILE"
    echo " Job : $JOB_NAME - Debut : $(date '+%H:%M:%S')" >> "$LOGFILE"
    echo "[INFO] Lancement de $JOB_NAME..."

    if [ ! -f "$JOB_SCRIPT" ]; then
        echo "[ERREUR] Fichier introuvable : $JOB_SCRIPT" | tee -a "$LOGFILE"
        echo "[ERREUR] Pipeline arrete."
        exit 1
    fi

    # Rendre le script executable si besoin
    chmod +x "$JOB_SCRIPT"

    # Executer le job et rediriger stdout + stderr vers le log
    "$JOB_SCRIPT" >> "$LOGFILE" 2>&1
    EXIT_CODE=$?

    if [ $EXIT_CODE -ne 0 ]; then
        echo " Job $JOB_NAME ECHEC - code $EXIT_CODE - $(date '+%H:%M:%S')" >> "$LOGFILE"
        echo "[ERREUR] $JOB_NAME a echoue (code $EXIT_CODE)"
        echo "[ERREUR] Pipeline arrete. Consultez : $LOGFILE"
        exit $EXIT_CODE
    fi

    echo " Job $JOB_NAME OK - Fin : $(date '+%H:%M:%S')" >> "$LOGFILE"
    echo "[OK] $JOB_NAME termine."
}

# ============================================================
#  EXECUTION DES 9 JOBS DANS L'ORDRE
# ============================================================

run_job "pays"       "$BASE_DIR/pays/pays_run.sh"
run_job "gare"       "$BASE_DIR/gare/gare_run.sh"
run_job "operateur"  "$BASE_DIR/operateur/operateur_run.sh"
run_job "type_train" "$BASE_DIR/type_train/type_train_run.sh"
run_job "ligne"      "$BASE_DIR/ligne/ligne_run.sh"
run_job "trajet"     "$BASE_DIR/trajet/trajet_run.sh"
run_job "exploite"   "$BASE_DIR/exploite/exploite_run.sh"
run_job "itineraire" "$BASE_DIR/itineraire/itineraire_run.sh"
run_job "emission"   "$BASE_DIR/emission/emission_run.sh"

# ============================================================
#  FIN DU PIPELINE
# ============================================================

echo "" >> "$LOGFILE"
echo "============================================================" >> "$LOGFILE"
echo " PIPELINE TERMINE AVEC SUCCES - $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOGFILE"
echo "============================================================" >> "$LOGFILE"

echo ""
echo "[OK] Pipeline ETL termine avec succes !"
echo "[OK] Consultez les logs : $LOGFILE"
exit 0

# ============================================================
#  PLANIFICATION CRON (a configurer une seule fois)
#  Commande : crontab -e
#  Ajouter la ligne suivante :
#
#  0 2 1 * * /opt/obRail/talend/run_etl.sh >> /var/log/obRail/cron.log 2>&1
#
#  Signification : le 1er de chaque mois a 02h00
# ============================================================