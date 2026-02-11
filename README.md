# Kimi K2.5 Multi-Agent Outreach System

Automated freelance client acquisition using Kimi K2.5's agent swarm capabilities. Targets $15K-$30K revenue in 90 days through organic LinkedIn and Reddit outreach.

## Quick Start

```bash
# 1. Initialize the system
cd /Users/cave/kimi_agent_system
python main.py init

# 2. Configure your settings
# Edit config/settings.json with your API keys and user info

# 3. Set up your profile
python main.py setup "Your Name" --title "AI Engineer | Analytics for SaaS" --linkedin "https://linkedin.com/in/yourprofile"

# 4. Run daily workflow
python main.py daily
```

## Architecture

```
┌─────────────────────────────────────────┐
│   ORCHESTRATOR AGENT (Kimi K2.5 Core)   │
│   • Goal decomposition                   │
│   • Task routing                         │
│   • Performance monitoring               │
└──────────────┬──────────────────────────┘
               │
      ┌────────┼────────┬─────────┬────────┐
      │        │        │         │        │
  ┌───▼──┐ ┌──▼──┐ ┌───▼───┐ ┌──▼───┐ ┌──▼───┐
  │ ICP  │ │Copy │ │Outreach│ │CRM   │ │Perf  │
  │Agent │ │Agent│ │ Agent  │ │Agent │ │Agent │
  └──────┘ └─────┘ └────────┘ └──────┘ └──────┘
```

### 5 Specialized Agents

1. **ICP Research Agent** (`agents/icp_research_agent.py`)
   - Researches 50 prospects/day (35 SaaS, 15 Agency)
   - Monitors Reddit for pain signals
   - Enriches prospect data

2. **Copy Generation Agent** (`agents/copy_generation_agent.py`)
   - Personalizes outreach messages using Kimi K2.5
   - Quality scoring (threshold: 7.0+)
   - 5 templates per niche (10 total)

3. **Outreach Execution Agent** (`agents/outreach_execution_agent.py`)
   - Schedules connection requests (max 20/day, 100/week)
   - 4-touch follow-up sequences
   - Safety limits to avoid LinkedIn restrictions

4. **CRM & Pipeline Agent** (`agents/crm_pipeline_agent.py`)
   - 10-stage pipeline tracking
   - Daily task generation
   - Auto-updates based on prospect actions

5. **Performance Optimization Agent** (`agents/performance_optimization_agent.py`)
   - Template A/B testing
   - Weekly performance reports
   - Strategy recommendations

## Daily Workflow

```
8:00 AM  - Morning Routine
  • Research 50 new prospects
  • Generate personalized messages
  • Create daily task list
  • Review yesterday's metrics

12:00 PM - Midday Execution
  • Send scheduled connection requests
  • Process incoming replies
  • Update pipeline stages

6:00 PM  - Evening Wrap-Up
  • Final outreach batch
  • Calculate daily metrics
  • Monitor Reddit for opportunities

Monday 8:00 AM - Weekly Review
  • Generate performance report
  • Analyze template performance
  • Compare niche performance
  • Output recommendations
```

## Commands

| Command | Description |
|---------|-------------|
| `python main.py morning` | Run morning routine only |
| `python main.py midday` | Execute scheduled outreach |
| `python main.py evening` | Run evening wrap-up |
| `python main.py daily` | Full daily workflow |
| `python main.py weekly` | Generate weekly report |
| `python main.py dashboard` | Show current dashboard |
| `python main.py setup "Name"` | Configure user profile |
| `python main.py init` | Initialize directories |

## Configuration

Edit `config/settings.json`:

```json
{
  "moonshot_api_key": "YOUR_KIMI_K2.5_API_KEY",
  "user_name": "Your Name",
  "user_title": "AI Engineer | Analytics for SaaS",
  "linkedin_profile_url": "https://linkedin.com/in/yourprofile",
  "niche_allocation": {
    "saas": 0.7,
    "agency": 0.3
  },
  "daily_limits": {
    "connections": 20,
    "messages": 20
  },
  "safety": {
    "weekly_connection_limit": 100,
    "min_delay_seconds": 300,
    "max_delay_seconds": 900
  },
  "quality_threshold": 7.0
}
```

## File Structure

```
kimi_agent_system/
├── agents/
│   ├── icp_research_agent.py
│   ├── copy_generation_agent.py
│   ├── outreach_execution_agent.py
│   ├── crm_pipeline_agent.py
│   ├── performance_optimization_agent.py
│   └── orchestrator.py
├── config/
│   └── settings.json
├── data/
│   ├── prospects.json
│   ├── tasks.json
│   ├── analytics.json
│   └── daily_reports/
├── templates/
│   ├── linkedin_outreach_saas.json
│   ├── linkedin_outreach_agency.json
│   ├── saas_offer_ladder.json
│   └── agency_offer_ladder.json
├── requirements.txt
└── main.py
```

## Data Files (from Downloads)

The system uses these files from `/Users/cave/Downloads/`:

- `Kimi-K2.5-Agent-Spec.md` - Full system specification
- `linkedin_outreach_saas.json` - 5 SaaS message templates
- `linkedin_outreach_agency.json` - 5 Agency message templates
- `saas_offer_ladder.json` - SaaS pricing and deliverables
- `agency_offer_ladder.json` - Agency pricing and deliverables
- `90_day_execution_plan.csv` - Weekly KPIs and targets
- `revenue_scenarios_saas_agency.csv` - Revenue projections

## LinkedIn Safety

- **Daily limit**: 20 connection requests
- **Weekly limit**: 100 connection requests
- **Delay between actions**: 5-15 minutes (randomized)
- **Optimal send times**: 9am, 12pm, 3pm, 6pm PT

## Performance Targets

| Metric | Target |
|--------|--------|
| Connection Acceptance Rate | >45% |
| Message Reply Rate | >20% |
| Qualified Lead Rate | >10% |
| Discovery Call Close Rate | >30% |
| 90-Day Revenue | $21K-$57K |

## Cost

- **Kimi K2.5 API**: ~$0.45/day ($13.50/month)
- **Total monthly cost**: $13.50-$43.50
- **ROI**: 165× (base case)

## Next Steps

1. Get Kimi K2.5 API key from https://platform.moonshot.ai
2. Set up LinkedIn automation (Phantombuster recommended)
3. Configure Airtable CRM (optional - JSON storage works too)
4. Test ICP Agent with 10 manual prospects
5. Review first 20 generated messages for quality
6. Launch Week 1 outreach

## License

MIT - Use at your own risk. Comply with LinkedIn ToS and anti-spam regulations.
