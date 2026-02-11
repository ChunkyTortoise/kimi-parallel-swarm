#!/usr/bin/env python3
"""
Parallel Agent Swarm - Quick Start Script
Initialize and run all 5 agents in parallel mode
"""
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.parallel_execution import AgentSwarmOrchestrator, ParallelAgentSwarm, AgentTask, AgentType
from utils.parallel_execution import run_agents_parallel


def print_banner():
    """Print startup banner."""
    print("""
╔════════════════════════════════════════════════════════════╗
║     🚀 PARALLEL AGENT SWARM - INITIALIZATION               ║
║     Mode: Parallel Execution | Target: 4.5× Speedup     ║
╚════════════════════════════════════════════════════════════╝
    """)


def load_config():
    """Load configuration."""
    config_path = Path("config/settings.json")
    
    if not config_path.exists():
        print("❌ Config not found. Run: python3 setup.py")
        sys.exit(1)
    
    with open(config_path) as f:
        return json.load(f)


def initialize_swarm(config: dict):
    """Initialize the parallel agent swarm."""
    print("📦 Initializing Agent Swarm...")
    
    orchestrator = AgentSwarmOrchestrator(config)
    orchestrator.initialize_agents()
    
    print("✅ All 5 agents registered and ready")
    print(f"   - ICP Research Agent")
    print(f"   - Copy Generation Agent")
    print(f"   - Outreach Execution Agent")
    print(f"   - CRM Pipeline Agent")
    print(f"   - Performance Optimization Agent")
    
    return orchestrator


def run_parallel_morning_routine(orchestrator):
    """Execute morning routine in parallel."""
    print("\n🌅 STARTING PARALLEL MORNING ROUTINE")
    print("-" * 50)
    
    start_time = datetime.now()
    
    # Execute parallel morning routine
    results = asyncio.run(orchestrator.execute_morning_routine_parallel())
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n✅ Parallel execution complete in {duration:.1f} seconds")
    
    # Display results
    print("\n📊 Results by Agent:")
    for task_id, result in results.items():
        if isinstance(result, dict):
            status = "✅" if result.get('success') else "❌"
            time_ms = result.get('time_ms', 0)
            print(f"   {status} {task_id}: {time_ms}ms")
    
    return results


def run_parallel_batch_demo(orchestrator):
    """Demo parallel batch processing."""
    print("\n📦 PARALLEL BATCH PROCESSING DEMO")
    print("-" * 50)
    print("Processing 50 prospects with maximum parallelism...")
    
    results = orchestrator.execute_parallel_batch(batch_size=50)
    
    print(f"\n✅ Batch complete")
    print(f"   Chunks processed: {results['chunks_processed']}")
    print(f"   Successful: {results['successful_chunks']}")
    print(f"   Total time: {results['total_time_seconds']:.1f}s")
    print(f"   Speedup: ~{results.get('speedup_vs_sequential', 0):.1f}× faster than sequential")


def display_parallel_stats(orchestrator):
    """Display swarm performance stats."""
    print("\n📈 PARALLEL SWARM STATS")
    print("-" * 50)
    
    stats = {
        "Max Workers": orchestrator.swarm.max_workers,
        "Use Processes": orchestrator.swarm.use_processes,
        "Agents Registered": len(orchestrator.swarm.agent_instances),
        "Queue Depth": len(orchestrator.swarm.task_queue),
        "Completed Tasks": len(orchestrator.swarm.results)
    }
    
    for key, value in stats.items():
        print(f"   {key}: {value}")


def main():
    """Main entry point."""
    print_banner()
    
    # Load config
    print("⚙️  Loading configuration...")
    config = load_config()
    print(f"   User: {config.get('user_name', 'Not Set')}")
    print(f"   API Key: {'✅ Set' if config.get('moonshot_api_key') else '❌ Missing'}")
    
    # Initialize swarm
    orchestrator = initialize_swarm(config)
    
    # Display stats
    display_parallel_stats(orchestrator)
    
    # Ask user what to run
    print("\n🎯 SELECT PARALLEL WORKFLOW:")
    print("   1. Morning Routine (Research + Messages)")
    print("   2. Batch Demo (50 Prospects Parallel)")
    print("   3. Custom Parallel Tasks")
    print("   4. Exit")
    
    choice = input("\nChoice (1-4): ").strip()
    
    if choice == "1":
        results = run_parallel_morning_routine(orchestrator)
        
        # Summary
        print("\n" + "=" * 50)
        print("📋 MORNING ROUTINE COMPLETE")
        print("=" * 50)
        
        saas_data = results.get('research_saas', {}).get('data') or []
        agency_data = results.get('research_agency', {}).get('data') or []
        
        if saas_data:
            print(f"✅ SaaS Prospects: {len(saas_data)}")
        if agency_data:
            print(f"✅ Agency Prospects: {len(agency_data)}")
        if 'message_generation' in results:
            print(f"✅ Messages Generated: {results['message_generation']}")
        
        print("\n🚀 Next: Run 'python3 main.py midday' to send outreach")
        
    elif choice == "2":
        run_parallel_batch_demo(orchestrator)
        
    elif choice == "3":
        print("\n📝 Custom parallel tasks - implement your own logic in:")
        print("   utils/parallel_execution.py")
        
    else:
        print("\n👋 Exiting. Run again anytime with: python3 run_parallel_swarm.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
