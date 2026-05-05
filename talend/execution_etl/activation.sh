#!/usr/bin/env bash
# Activation de l'ETL Talend — Linux uniquement
# Pour Windows, utiliser talend/lancement/lancement.bat

set -euo pipefail

cd ./talend/lancement || exit 1
./lancement.sh
