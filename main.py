"""
Kimi K2.5 Multi-Agent Outreach System
Main entry point for running the agent swarm.
"""
import os
import sys
import json
import click
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.orchestrator import AgentOrchestrator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@click.group()
@click.option('--config', default='config/settings.json', help='Path to config file')
@click.pass_context
def cli(ctx, config):
    """Kimi K2.5 Multi-Agent Outreach System"""
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = config
    
    # Ensure data directory exists
    Path('data').mkdir(exist_ok=True)


@cli.command()
@click.pass_context
def morning(ctx):
    """Run morning routine (research, message generation, task list)"""
    click.echo("☀️  Starting morning routine...")
    
    orchestrator = AgentOrchestrator(ctx.obj['config_path'])
    results = orchestrator.morning_routine()
    
    click.echo(f"\n✅ Morning routine complete!")
    click.echo(f"   New prospects: {results['new_prospects']}")
    click.echo(f"   Messages ready: {results['messages_ready']}")
    click.echo(f"   Avg quality score: {results.get('avg_quality_score', 0):.1f}")
    click.echo(f"   Priority tasks: {results['priority_tasks']}")
    click.echo(f"   High-priority leads: {results['high_priority_leads']}")


@cli.command()
@click.pass_context
def midday(ctx):
    """Run midday execution (send scheduled outreach)"""
    click.echo("🌤  Starting midday execution...")
    
    orchestrator = AgentOrchestrator(ctx.obj['config_path'])
    results = orchestrator.midday_execution()
    
    click.echo(f"\n✅ Midday execution complete!")
    click.echo(f"   Actions executed: {results['actions_executed']}")


@cli.command()
@click.pass_context
def evening(ctx):
    """Run evening wrap-up (final batch, metrics, reporting)"""
    click.echo("🌙 Starting evening wrap-up...")
    
    orchestrator = AgentOrchestrator(ctx.obj['config_path'])
    results = orchestrator.evening_wrapup()
    
    click.echo(f"\n✅ Evening wrap-up complete!")
    click.echo(f"   Final actions: {results['final_actions']}")
    click.echo(f"   Pipeline value: ${results.get('pipeline_value', 0):,}")
    click.echo(f"   Reddit opportunities: {results['reddit_opportunities']}")


@cli.command()
@click.pass_context
def daily(ctx):
    """Run full daily workflow (morning + midday + evening)"""
    click.echo("🚀 Running full daily workflow...")
    
    orchestrator = AgentOrchestrator(ctx.obj['config_path'])
    results = orchestrator.run_full_day()
    
    click.echo(f"\n✅ Daily workflow complete!")
    click.echo(f"\nMorning:")
    click.echo(f"   Prospects: {results['morning']['new_prospects']}")
    click.echo(f"   Messages: {results['morning']['messages_ready']}")
    click.echo(f"\nMidday:")
    click.echo(f"   Executed: {results['midday']['actions_executed']}")
    click.echo(f"\nEvening:")
    click.echo(f"   Final actions: {results['evening']['final_actions']}")
    click.echo(f"   Pipeline: ${results['evening'].get('pipeline_value', 0):,}")


@cli.command()
@click.pass_context
def weekly(ctx):
    """Generate weekly performance report"""
    click.echo("📊 Generating weekly report...")
    
    orchestrator = AgentOrchestrator(ctx.obj['config_path'])
    report = orchestrator.weekly_review()
    
    click.echo(f"\n📈 Weekly Report ({report['report_date'][:10]})")
    click.echo(f"\nSummary:")
    summary = report['summary']
    click.echo(f"   Connections sent: {summary['connections_sent']}")
    click.echo(f"   Acceptance rate: {summary['acceptance_rate']}")
    click.echo(f"   Reply rate: {summary['reply_rate']}")
    click.echo(f"   Deals closed: {summary['deals_closed']}")
    click.echo(f"   Revenue: {summary['revenue']}")
    
    if report['alerts']:
        click.echo(f"\n⚠️  Alerts:")
        for alert in report['alerts']:
            click.echo(f"   - {alert}")
    
    if report['recommendations']:
        click.echo(f"\n💡 Recommendations:")
        for rec in report['recommendations'][:3]:
            priority = "🔴" if rec['priority'] == 'high' else "🟡"
            click.echo(f"   {priority} {rec['issue']}: {rec['action']}")


@cli.command()
@click.pass_context
def dashboard(ctx):
    """Show current system dashboard"""
    orchestrator = AgentOrchestrator(ctx.obj['config_path'])
    dash = orchestrator.get_dashboard()
    
    click.echo(f"\n📊 System Dashboard ({dash['timestamp'][:10]})")
    click.echo(f"\nDaily Limits:")
    limits = dash['daily_limits']
    click.echo(f"   Connections: {limits['connections_sent_today']}/{limits['connections_limit']}")
    click.echo(f"   Messages: {limits['messages_sent_today']}/{limits['messages_limit']}")
    click.echo(f"   Weekly: {limits['weekly_connections']}/{limits['weekly_limit']}")
    
    click.echo(f"\nPipeline:")
    pipeline = dash['pipeline']
    click.echo(f"   Total prospects: {pipeline['total_prospects']}")
    click.echo(f"   Pipeline value: ${pipeline['pipeline_value']:,}")
    click.echo(f"   Qualified leads: {pipeline['qualified_leads']}")
    click.echo(f"   Discovery calls: {pipeline['discovery_calls_booked']}")
    click.echo(f"   Proposals sent: {pipeline['proposals_sent']}")
    click.echo(f"   Deals won: {pipeline['deals_won']}")
    
    click.echo(f"\nTasks:")
    click.echo(f"   Today's tasks: {dash['today_tasks']}")
    click.echo(f"   Action queue: {dash['queue_length']}")


@cli.command()
@click.argument('name')
@click.option('--title', default='AI Engineer', help='Your professional title')
@click.option('--linkedin', default='', help='Your LinkedIn profile URL')
def setup(name, title, linkedin):
    """Setup configuration file with user info"""
    config_path = Path('config/settings.json')
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    config['user_name'] = name
    config['user_title'] = title
    config['linkedin_profile_url'] = linkedin
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    click.echo(f"✅ Configuration updated for {name}")
    click.echo(f"   Title: {title}")
    click.echo(f"   LinkedIn: {linkedin if linkedin else 'Not set'}")


@cli.command()
def init():
    """Initialize system directories and files"""
    dirs = ['data', 'config', 'templates']
    
    for d in dirs:
        Path(d).mkdir(exist_ok=True)
        click.echo(f"✅ Created {d}/")
    
    # Copy templates from Downloads if available
    templates_source = Path('/Users/cave/Downloads')
    templates_dest = Path('templates')
    
    for template_file in ['linkedin_outreach_saas.json', 'linkedin_outreach_agency.json', 
                          'saas_offer_ladder.json', 'agency_offer_ladder.json']:
        source = templates_source / template_file
        dest = templates_dest / template_file
        
        if source.exists() and not dest.exists():
            import shutil
            shutil.copy(source, dest)
            click.echo(f"✅ Copied {template_file}")
    
    click.echo(f"\n🎉 System initialized!")
    click.echo(f"   Next: Set your API keys in config/settings.json")
    click.echo(f"   Then: Run 'python main.py setup \"Your Name\"'")


if __name__ == '__main__':
    cli()
