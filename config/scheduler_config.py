"""
Cron Job Setup for Daily Automation
Add these to your crontab or use with APScheduler
"""

# ==========================================
# CRONTAB ENTRIES (run: crontab -e)
# ==========================================

# Morning Routine - 8:00 AM PT (15:00 UTC)
0 15 * * * cd /Users/cave/kimi_agent_system && /usr/bin/python3 run_parallel_swarm.py << 'EOF'
1
EOF

# Midday Check - 1:00 PM PT (20:00 UTC)
0 20 * * * cd /Users/cave/kimi_agent_system && /usr/bin/python3 main.py midday >> logs/midday.log 2>&1

# Evening Wrap - 5:00 PM PT (00:00 UTC next day)
0 0 * * * cd /Users/cave/kimi_agent_system && /usr/bin/python3 main.py evening >> logs/evening.log 2>&1

# Performance Report - Daily at 6:00 PM PT (01:00 UTC)
0 1 * * * cd /Users/cave/kimi_agent_system && /usr/bin/python3 -c "
from utils.parallel_execution import AgentSwarmOrchestrator
from config import load_config
import json
config = load_config()
orchestrator = AgentSwarmOrchestrator(config)
report = orchestrator.generate_performance_report()
print(json.dumps(report, indent=2))
" >> logs/performance.log 2>&1

# ==========================================
# APScheduler Alternative (Python-based)
# ==========================================

SCHEDULER_CONFIG = {
    "jobs": [
        {
            "id": "morning_routine",
            "name": "Morning Routine",
            "trigger": "cron",
            "hour": 8,
            "minute": 0,
            "timezone": "America/Los_Angeles",
            "function": "run_morning_routine"
        },
        {
            "id": "midday_check",
            "name": "Midday Check",
            "trigger": "cron", 
            "hour": 13,
            "minute": 0,
            "timezone": "America/Los_Angeles",
            "function": "run_midday_check"
        },
        {
            "id": "evening_wrap",
            "name": "Evening Wrap",
            "trigger": "cron",
            "hour": 17,
            "minute": 0,
            "timezone": "America/Los_Angeles",
            "function": "run_evening_wrap"
        },
        {
            "id": "performance_report",
            "name": "Daily Performance Report",
            "trigger": "cron",
            "hour": 18,
            "minute": 0,
            "timezone": "America/Los_Angeles",
            "function": "generate_report"
        }
    ],
    "settings": {
        "misfire_grace_time": 3600,  # 1 hour
        "coalesce": True,
        "max_instances": 1,
        "job_defaults": {
            "retry_count": 3,
            "retry_delay": 300  # 5 minutes
        }
    }
}

# ==========================================
# SYSTEMD SERVICE (Linux servers)
# ==========================================

SYSTEMD_SERVICE = """
[Unit]
Description=Kimi Agent Swarm Scheduler
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/Users/cave/kimi_agent_system
ExecStart=/usr/bin/python3 scheduler_daemon.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/Users/cave/kimi_agent_system

[Install]
WantedBy=multi-user.target
"""

# Save to: /etc/systemd/system/kimi-scheduler.service
# Then: sudo systemctl enable kimi-scheduler && sudo systemctl start kimi-scheduler

# ==========================================
# LAUNCHD (macOS)
# ==========================================

LAUNCHD_PLIST = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.kimi.agent.scheduler</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/cave/kimi_agent_system/scheduler_daemon.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
        <dict>
            <key>Hour</key>
            <integer>8</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
    </array>
    <key>StandardOutPath</key>
    <string>/Users/cave/kimi_agent_system/logs/scheduler.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/cave/kimi_agent_system/logs/scheduler_error.log</string>
</dict>
</plist>
"""

# Save to: ~/Library/LaunchAgents/com.kimi.agent.scheduler.plist
# Then: launchctl load ~/Library/LaunchAgents/com.kimi.agent.scheduler.plist

if __name__ == "__main__":
    import json
    print("Scheduler Configuration:")
    print(json.dumps(SCHEDULER_CONFIG, indent=2))
