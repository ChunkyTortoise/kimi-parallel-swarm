# DEPLOYMENT GUIDE
# Kimi K2.5 Multi-Agent Outreach System

## Quick Deploy (5 minutes)

```bash
# 1. Navigate to project
cd /Users/cave/kimi_agent_system

# 2. Run setup wizard
python3 setup.py

# 3. Verify installation
python3 test_system.py

# 4. Start monitoring dashboard (optional)
python3 dashboard.py &

# 5. Start automated scheduler
python3 scheduler.py
```

## Docker Deploy

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Manual Deploy (Detailed)

### Step 1: Provision Infrastructure

**Kimi K2.5 API**
1. Visit https://platform.moonshot.ai
2. Sign up for developer account
3. Create API key
4. Add to `config/settings.json` or `.env`

**LinkedIn Automation (Phantombuster)**
1. Visit https://phantombuster.com
2. Start free trial ($30/mo after)
3. Get API key
4. Optional: Use Waalaxy free tier (100 connections/week)

**Airtable CRM (Optional)**
1. Visit https://airtable.com/create
2. Create new base
3. Get API key from https://airtable.com/create/tokens
4. Get Base ID from https://airtable.com/api
5. Run: `python3 utils/airtable.py` for setup instructions

**Reddit API (Optional)**
1. Visit https://www.reddit.com/prefs/apps
2. Create app
3. Get Client ID and Secret

### Step 2: Configure System

```bash
# Run interactive setup
python3 setup.py

# Or manual edit
nano config/settings.json
```

**Required fields:**
- `moonshot_api_key` - Required for all operations
- `user_name` - Your name for signatures
- `user_title` - Professional title
- `niche_allocation` - SaaS/Agency split (default 70/30)

### Step 3: Test Core Components

```bash
# Test all imports and connections
python3 test_system.py

# Test individual agents
python3 agents/icp_research_agent.py
python3 agents/copy_generation_agent.py
python3 agents/crm_pipeline_agent.py

# Test utilities
python3 utils/rate_limit_monitor.py --report
```

### Step 4: Import Initial Prospects (Optional)

```bash
# From CSV
python3 utils/import_export.py import-csv prospects.csv --niche saas

# From LinkedIn URLs list
python3 utils/import_export.py import-linkedin urls.txt --niche agency
```

### Step 5: Launch Week 1 (Calibration Phase)

**Day 1-3: Manual Testing**
```bash
# Run morning routine (research + message generation)
python3 main.py morning

# Review generated messages in data/prospects.json
# Verify quality score > 7.0

# Run midday (send test batch of 5-10)
python3 main.py midday

# Monitor acceptance rates
python3 utils/rate_limit_monitor.py --report
```

**Day 4-7: Ramp Up**
```bash
# Full daily workflow
python3 main.py daily

# Check dashboard
python3 main.py dashboard
```

### Step 6: Full Automation (Week 2+)

```bash
# Start automated scheduler
# Runs daily at: 8am, 12pm, 6pm PT
python3 scheduler.py

# Or use Docker (recommended for production)
docker-compose up -d
```

## Monitoring

### Dashboard
```bash
# Web dashboard (localhost:8080)
python3 dashboard.py

# Or with custom port
python3 dashboard.py --port 3000
```

### CLI Commands
```bash
# View system status
python3 main.py dashboard

# Check rate limits
python3 utils/rate_limit_monitor.py --report

# View logs
tail -f data/system.log

# Weekly report
python3 main.py weekly
```

### Makefile Shortcuts
```bash
make setup          # Run setup wizard
make test           # Run tests
make dashboard      # Show dashboard
make daily          # Run daily workflow
make schedule       # Start scheduler
make logs           # View logs
make backup         # Backup data
make stats          # Quick stats
```

## Troubleshooting

### Issue: "No module named 'requests'"
**Fix:** `pip3 install -r requirements.txt`

### Issue: "Kimi API error"
**Fix:** Verify `moonshot_api_key` in config/settings.json

### Issue: "LinkedIn rate limited"
**Fix:** 
1. Check status: `python3 utils/rate_limit_monitor.py --report`
2. Wait 24 hours
3. Reduce daily limits in config

### Issue: "No prospects found"
**Fix:** Run `python3 main.py morning` to generate initial prospects

### Issue: "Docker container exits immediately"
**Fix:** Check logs: `docker-compose logs`

## Backup & Recovery

```bash
# Manual backup
make backup

# Or manually
tar -czf backup-$(date +%Y%m%d).tar.gz data/ config/

# Restore
tar -xzf backup-YYYYMMDD.tar.gz
```

## Security Best Practices

1. **Never commit API keys**
   - Keep `.env` in `.gitignore`
   - Use `config/settings.json` for non-secrets

2. **Rotate API keys monthly**
   - Kimi K2.5: https://platform.moonshot.ai
   - Phantombuster: https://phantombuster.com

3. **Monitor account health**
   - Check LinkedIn restrictions weekly
   - Review rate limit logs daily

4. **Data privacy**
   - Prospect data stored locally in `data/`
   - No data sent to third parties except:
     - Kimi K2.5 (message generation)
     - Phantombuster (LinkedIn automation)
     - Airtable (if configured)

## Performance Optimization

### Week 1-2: Baseline
- Monitor acceptance rates (target >40%)
- Review first 20 messages manually
- Adjust templates if reply rate <15%

### Week 3-4: Optimize
- Performance Agent analyzes bottlenecks
- A/B test new templates
- Adjust niche allocation based on data

### Week 5+: Scale
- Increase to full 50 prospects/day
- Add cold email channel for non-responders
- Refine ICP criteria based on close rates

## Cost Tracking

| Service | Monthly Cost | Notes |
|---------|--------------|-------|
| Kimi K2.5 API | ~$13.50 | ~900K tokens/day |
| Phantombuster | $30 | Starter plan |
| Airtable | $0 | Free tier (<1K records) |
| **Total** | **$43.50** | Base case ROI: 165× |

## 90-Day Success Metrics

| Week | Connections | Calls | Proposals | Closes | Revenue |
|------|---------------|-------|-----------|--------|---------|
| 1-2  | 60            | 0     | 0         | 0      | $0      |
| 3-4  | 140           | 4     | 0         | 0      | $0      |
| 5-6  | 200           | 8     | 2         | 1      | $6K     |
| 7-8  | 200           | 12    | 3         | 1      | $12K    |
| 9-10 | 200           | 16    | 4         | 2      | $24K    |
| 11-12| 200           | 20    | 5         | 2      | $24K    |
| **Total** | **1,000** | **60** | **14** | **6** | **$66K** |

## Support & Resources

- **Documentation:** README.md
- **System Spec:** /Users/cave/Downloads/Kimi-K2.5-Agent-Spec.md
- **Templates:** /Users/cave/Downloads/linkedin_outreach_*.json
- **Offer Ladders:** /Users/cave/Downloads/*_offer_ladder.json
- **Kimi K2.5 Docs:** https://platform.moonshot.ai/docs

## Next Steps After Deploy

1. ✅ Review generated messages for quality
2. ✅ Send first 10 test connections
3. ✅ Monitor acceptance rate for 48 hours
4. ✅ Write first 5-10 DMs manually to train voice
5. ✅ Post helpful comments on Reddit (r/SaaS, r/startups)
6. ✅ Book first discovery call
7. ✅ Close first deal 🎉

---

**You are ready to launch! Good luck! 🚀**
