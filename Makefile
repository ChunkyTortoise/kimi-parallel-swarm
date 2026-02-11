.PHONY: help install test setup run daily weekly dashboard docker clean

# Default target
help: ## Show this help message
	@echo "Kimi K2.5 Agent System - Available Commands"
	@echo "=========================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	pip3 install -r requirements.txt

setup: ## Run interactive setup wizard
	python3 setup.py

test: ## Run system tests
	python3 test_system.py

dashboard: ## Show current system dashboard
	python3 main.py dashboard

morning: ## Run morning routine (research + message generation)
	python3 main.py morning

midday: ## Run midday execution (send scheduled outreach)
	python3 main.py midday

evening: ## Run evening wrap-up (metrics + reporting)
	python3 main.py evening

daily: ## Run full daily workflow
	python3 main.py daily

weekly: ## Generate weekly performance report
	python3 main.py weekly

schedule: ## Start automated scheduler (runs daily at 8am, 12pm, 6pm)
	python3 scheduler.py

schedule-once: ## Run scheduler once for testing
	python3 scheduler.py --run-once morning

docker-build: ## Build Docker image
	docker build -t kimi-agent:latest .

docker-run: ## Run in Docker container
	docker run -d \
		--name kimi-agent \
		-v $(PWD)/data:/app/data \
		-v $(PWD)/config:/app/config \
		-v $(PWD)/.env:/app/.env:ro \
		--restart unless-stopped \
		kimi-agent:latest

docker-compose: ## Run with docker-compose
	docker-compose up -d

docker-compose-logs: ## View docker-compose logs
	docker-compose logs -f

docker-stop: ## Stop Docker containers
	docker stop kimi-agent || true
	docker-compose down || true

logs: ## View system logs
	tail -f data/system.log

clean: ## Clean up temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	rm -rf .pytest_cache 2>/dev/null || true

backup: ## Backup data directory
	@mkdir -p backups
	@tar -czf backups/kimi-agent-backup-$(shell date +%Y%m%d-%H%M%S).tar.gz data/ config/
	@echo "Backup created in backups/"

stats: ## Show quick stats
	@echo "Quick Stats"
	@echo "=========="
	@python3 -c "
	import json
	from pathlib import Path
	
	# Count prospects
	prospects_file = Path('data/prospects.json')
	if prospects_file.exists():
		with open(prospects_file) as f:
			prospects = json.load(f)
		print(f'Prospects: {len(prospects)}')
		
		# Stage breakdown
		stages = {}
		for p in prospects.values():
			stage = p.get('stage', 'unknown')
			stages[stage] = stages.get(stage, 0) + 1
		
		for stage, count in sorted(stages.items()):
			print(f'  - {stage}: {count}')
	else:
		print('Prospects: 0 (no data yet)')
	
	# Count reports
	reports_dir = Path('data/daily_reports')
	if reports_dir.exists():
		reports = list(reports_dir.glob('report_*.json'))
		print(f'\nDaily reports: {len(reports)}')
	"

lint: ## Run Python linting
	flake8 agents/ utils/ --max-line-length=120 --ignore=E501,W503 || true
	@echo "Lint check complete"
