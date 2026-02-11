#!/usr/bin/env python3
"""
Quick test script for the Kimi Agent System
Tests each agent individually without API calls
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_agents():
    print("🧪 Testing Kimi Agent System...\n")
    
    # Test imports
    try:
        from agents.icp_research_agent import ICPResearchAgent, Prospect
        from agents.copy_generation_agent import CopyGenerationAgent
        from agents.outreach_execution_agent import OutreachExecutionAgent
        from agents.crm_pipeline_agent import CRMPipelineAgent
        from agents.performance_optimization_agent import PerformanceOptimizationAgent
        from agents.orchestrator import AgentOrchestrator
        print("✅ All agent imports successful\n")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return
    
    # Test config loading
    try:
        config_path = Path("config/settings.json")
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
            print(f"✅ Config loaded: {len(config)} settings\n")
        else:
            print("⚠️  Config not found - run 'python main.py init' first\n")
            config = {}
    except Exception as e:
        print(f"❌ Config error: {e}\n")
        config = {}
    
    # Test CRM Agent (no API key needed for basic ops)
    try:
        crm = CRMPipelineAgent(config)
        print(f"✅ CRM Agent initialized")
        print(f"   - Prospects loaded: {len(crm.prospects)}")
        print(f"   - Tasks loaded: {len(crm.tasks)}\n")
    except Exception as e:
        print(f"❌ CRM Agent error: {e}\n")
    
    # Test template loading
    templates = [
        "/Users/cave/Downloads/linkedin_outreach_saas.json",
        "/Users/cave/Downloads/linkedin_outreach_agency.json"
    ]
    
    for template_file in templates:
        if Path(template_file).exists():
            with open(template_file) as f:
                data = json.load(f)
            print(f"✅ {Path(template_file).name}: {len(data)} templates")
        else:
            print(f"⚠️  {Path(template_file).name}: not found")
    print()
    
    # Test offer ladders
    ladders = [
        "/Users/cave/Downloads/saas_offer_ladder.json",
        "/Users/cave/Downloads/agency_offer_ladder.json"
    ]
    
    for ladder_file in ladders:
        if Path(ladder_file).exists():
            with open(ladder_file) as f:
                data = json.load(f)
            print(f"✅ {Path(ladder_file).name}: {len(data)} offers")
        else:
            print(f"⚠️  {ladder_file.name}: not found")
    print()
    
    print("=" * 50)
    print("🎉 System test complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Add your Kimi K2.5 API key to config/settings.json")
    print("2. Run: python main.py setup 'Your Name'")
    print("3. Run: python main.py dashboard")
    print("4. Run: python main.py daily")


if __name__ == "__main__":
    test_agents()
