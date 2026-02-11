# Kimi Parallel Agent Swarm - Complete Documentation

## Quick Start (5 minutes)

```bash
# Clone repository
git clone https://github.com/ChunkyTortoise/kimi-parallel-swarm.git
cd kimi-parallel-swarm

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run parallel swarm
python3 run_parallel_swarm.py
```

## Architecture

```
┌─────────────────────────────────────────────┐
│           Parallel Agent Swarm              │
├─────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │ ICP     │ │ Copy    │ │ Outreach│       │
│  │ Research│ │ Generate│ │ Execute │       │
│  └─────────┘ └─────────┘ └─────────┘       │
│  ┌─────────┐ ┌─────────┐                   │
│  │ CRM     │ │Performance│                  │
│  │ Pipeline│ │   Opt    │                   │
│  └─────────┘ └─────────┘                   │
└─────────────────────────────────────────────┘
              ↓ 10× Parallel Speedup
┌─────────────────────────────────────────────┐
│  Streamlit Dashboard | Scheduler | APIs     │
└─────────────────────────────────────────────┘
```

## Agents Reference

### 1. ICP Research Agent
- **Purpose**: Find ideal prospects on LinkedIn and Reddit
- **Parallel**: Researches 10 prospects simultaneously
- **Output**: Qualified leads with quality scores

### 2. Copy Generation Agent  
- **Purpose**: Creates personalized LinkedIn messages
- **Input**: Prospect data from ICP Research
- **Output**: 10/10 quality personalized messages

### 3. Outreach Execution Agent
- **Purpose**: Sends LinkedIn connections and messages
- **Safety**: Rate limiting, daily caps (20 connections)
- **Integration**: Phantombuster API

### 4. CRM Pipeline Agent
- **Purpose**: Manages deal flow in Airtable/Salesforce
- **Features**: Stage tracking, automated updates
- **Reports**: Pipeline value, conversion metrics

### 5. Performance Optimization Agent
- **Purpose**: Analyzes metrics and suggests improvements
- **Frequency**: Daily analysis
- **Output**: Actionable optimization recommendations

## API Reference

### Parallel Execution Engine

```python
from utils.parallel_execution import AgentSwarmOrchestrator

# Initialize
orchestrator = AgentSwarmOrchestrator(config)
orchestrator.initialize_agents()

# Run morning routine in parallel
results = asyncio.run(orchestrator.execute_morning_routine_parallel())

# Batch process 50 prospects
results = asyncio.run(
    orchestrator.execute_batch_parallel(prospects, max_workers=10)
)
```

### CRM Integrations

```python
from utils.crm_integrations import HubSpotIntegration, SalesforceIntegration

# HubSpot
hubspot = HubSpotIntegration(api_key="your_key")
hubspot.create_contact(prospect_data)

# Salesforce
sf = SalesforceIntegration(
    client_id="...", client_secret="...",
    username="...", password="...", security_token="..."
)
sf.create_lead(prospect_data)
```

## Configuration

### Environment Variables (.env)

```bash
# Required
MOONSHOT_API_KEY=your_moonshot_api_key_here

# Optional Integrations
PHANTOMBUSTER_API_KEY=your_key
AIRTABLE_API_KEY=your_key
SALESFORCE_CLIENT_ID=your_id
HUBSPOT_API_KEY=your_key

# User Profile
USER_NAME=Your Name
USER_TITLE=Your Title
LINKEDIN_PROFILE_URL=https://linkedin.com/in/you
```

### Scheduler Setup

```bash
# Option 1: Cron (simplest)
crontab -e
# Add: 0 15 * * * cd /path && python3 run_parallel_swarm.py

# Option 2: APScheduler (Python)
python3 scheduler.py

# Option 3: Systemd service (servers)
sudo systemctl enable kimi-scheduler
```

## Dashboard

```bash
# Start Streamlit dashboard
streamlit run streamlit_dashboard.py

# Access at http://localhost:8501
```

Features:
- Real-time agent status
- Performance metrics
- Pipeline visualization
- Quick action buttons

## Deployment

### Local Machine
```bash
python3 setup.py
python3 run_parallel_swarm.py
```

### Docker
```bash
docker-compose up -d
```

### Cloud (AWS/GCP)
See `DEPLOYMENT.md` for detailed instructions.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API key errors | Check .env file, regenerate keys |
| Rate limiting | Increase MIN_DELAY_SECONDS in .env |
| No prospects found | Verify LinkedIn session cookie |
| CRM sync failing | Check Airtable base ID and permissions |

## Performance Benchmarks

| Task | Sequential | Parallel | Speedup |
|------|------------|----------|---------|
| 50 prospects | 15 min | 3 min | **5×** |
| 20 messages | 10 min | 1 min | **10×** |
| Morning routine | 35 min | 5 min | **7×** |

## Support

- **GitHub Issues**: https://github.com/ChunkyTortoise/kimi-parallel-swarm/issues
- **Documentation**: This file
- **Changelog**: See git log

## License

MIT License - See LICENSE file
