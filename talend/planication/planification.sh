#!/bin/bash
# ============================================================
#  ObRail Europe - Installation de la planification mensuelle
#  Equivalent de installer_tache_planifiee.bat pour Linux
#  Configure le cron pour lancer lancement.sh le 1er du mois
#  DOIT ETRE EXECUTE EN TANT QUE ROOT (une seule fois)
# ============================================================

# --- CONFIGURATION ---
ETL_SCRIPT="./talend/lancement/lancement.sh"
LOG_DIR="./talend/logs"
CRON_LOG="$LOG_DIR/cron.log"
CRON_LINE="0 2 1 * * $ETL_SCRIPT >> $CRON_LOG 2>&1"
# ---------------------

echo ""
echo "============================================================"
echo " ObRail Europe - Installation de la planification cron"
echo "============================================================"
echo ""

# Verifier les droits root
if [ "$EUID" -ne 0 ]; then
    echo "[ERREUR] Ce script doit etre execute en tant que root."
    echo "[ERREUR] Relancez avec : sudo bash installer_planification.sh"
    exit 1
fi

echo "[INFO] Droits root confirmes."

# Verifier que lancement.sh existe
if [ ! -f "$ETL_SCRIPT" ]; then
    echo "[ERREUR] Fichier introuvable : $ETL_SCRIPT"
    echo "[ERREUR] Verifiez le chemin dans la section CONFIGURATION de ce script."
    exit 1
fi

echo "[INFO] Script ETL trouve : $ETL_SCRIPT"

# Rendre lancement.sh executable si besoin
chmod +x "$ETL_SCRIPT"
echo "[INFO] Permissions d'execution confirmees sur $ETL_SCRIPT"

# Creer le dossier de logs s'il n'existe pas
mkdir -p "$LOG_DIR"
echo "[INFO] Dossier de logs : $LOG_DIR"

# Verifier si la tache cron existe deja
crontab -l 2>/dev/null | grep -q "$ETL_SCRIPT"
if [ $? -eq 0 ]; then
    echo "[INFO] Une tache cron existante a ete trouvee. Remplacement en cours..."
    # Supprimer l'ancienne ligne et ajouter la nouvelle
    (crontab -l 2>/dev/null | grep -v "$ETL_SCRIPT"; echo "$CRON_LINE") | crontab -
else
    # Ajouter la nouvelle ligne au crontab
    (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
fi

if [ $? -ne 0 ]; then
    echo "[ERREUR] Echec de l'installation de la tache cron."
    exit 1
fi

echo ""
echo "============================================================"
echo " INSTALLATION REUSSIE"
echo "============================================================"
echo ""
echo " Script execute   : $ETL_SCRIPT"
echo " Planification    : Le 1er de chaque mois a 02h00"
echo " Log cron         : $CRON_LOG"
echo ""
echo " Pour verifier la tache installee :"
echo "   crontab -l"
echo ""
echo " Pour supprimer la tache :"
echo "   crontab -l | grep -v '$ETL_SCRIPT' | crontab -"
echo ""
echo " Pour tester immediatement le pipeline :"
echo "   bash $ETL_SCRIPT"
echo ""
echo "============================================================"
echo ""
exit 0