.DEFAULT_GOAL := help
.PHONY: help up down restart logs ps build clean \
        frontend-dev frontend-test \
        backend-dev backend-test backend-shell \
        etl-run etl-validate \
        db-shell db-dump db-restore \
        monitoring ci-local

BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RESET := \033[0m

## Affiche cette aide
help: 
	@echo ""
	@echo "$(GREEN)ObRail Europe — Commandes disponibles$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-22s$(RESET) %s\n", $$1, $$2}'
	@echo ""

#  Stack complète 

## Lance toute la stack
up: 
	docker compose up -d --build
	@echo ""
	@echo "$(GREEN)Stack démarrée :$(RESET)"
	@echo "   Frontend  → http://localhost:8501"
	@echo "   Backend   → http://localhost:8000/docs"
	@echo "   Grafana   → http://localhost:3010  (admin / admin)"
	@echo ""

## Arrête tout
down: 
	docker compose down

## Redémarre
restart: down up 

## Logs continus  make logs SVC=backend pour un service
logs: 
	docker compose logs -f $(SVC)

## Liste les containers
ps: 
	docker compose ps

## Rebuild sans cache
build: 
	docker compose build --no-cache

## Stoppe + supprime volumes (perte de données)
clean: 
	docker compose down -v

#  Frontend Streamlit 

## Lance Streamlit en local
frontend-dev: 
	cd dashboard && streamlit run app.py

frontend-test: ## Tests pytest
	cd dashboard && pytest tests/ -v

#  Backend 

## Lance uvicorn en mode dev
backend-dev: 
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

## Tests pytest backend
backend-test: 
	cd backend && pytest -v

## Shell Python dans le container
backend-shell: 
	docker compose exec backend python

#  ETL Talend 

## Lance le pipeline ETL Talend (Linux)
etl-run: 
	cd talend/lancement && bash lancement.sh

## Vérifie la structure des 9 jobs
etl-validate: 
	@echo "Vérification..."
	@for job in pays gare operateur type_train ligne trajet exploite itineraire emission; do \
		if [ ! -f "talend/Jobs/Jobs/$$job/$${job}_0_1.jar" ]; then \
			echo " Manquant : $$job"; exit 1; \
		fi; \
	done
	@echo "Tous les 9 jobs OK"

#  Database 
## psql dans le container
db-shell: 
	docker compose exec postgres psql -U postgres -d mspr2

## Génère un dump SQL daté
db-dump: 
	@DATESTAMP=$$(date +%Y-%m-%d_%H%M%S); \
	docker compose exec postgres pg_dump -U postgres -d mspr2 \
		> talend/dump/mspr2_dump_$$DATESTAMP.sql && \
	echo "talend/dump/mspr2_dump_$$DATESTAMP.sql"

## Restaure le dump le plus récent
db-restore: 
	@FILE=$${FILE:-$$(ls -t talend/dump/*.sql | head -1)}; \
	docker compose exec -T postgres psql -U postgres -d mspr2 < $$FILE && \
	echo "Restauré"

#  Monitoring 

## Ouvre Grafana
monitoring: 
	@command -v xdg-open >/dev/null 2>&1 && xdg-open http://localhost:3010 || \
	command -v open >/dev/null 2>&1 && open http://localhost:3010 || \
	echo "Ouvrir : http://localhost:3010"

#  CI locale 
ci-local: etl-validate frontend-test backend-test 
	@echo ""
	@echo "$(GREEN)CI locale OK — tu peux push.$(RESET)"
