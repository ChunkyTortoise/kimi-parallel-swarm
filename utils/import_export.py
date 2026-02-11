"""
Prospect Import/Export Utilities
Handle CSV, JSON, and manual LinkedIn list imports
"""
import json
import csv
import argparse
from pathlib import Path
from datetime import datetime


def import_from_csv(filepath: str, niche: str = "saas"):
    """Import prospects from CSV file."""
    prospects = []
    
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            prospect = {
                "prospect_id": f"import_{hash(row.get('linkedin_url', '')) % 1000000}",
                "name": row.get('name', ''),
                "title": row.get('title', ''),
                "company": row.get('company', ''),
                "linkedin_url": row.get('linkedin_url', ''),
                "email": row.get('email', ''),
                "niche": niche,
                "source": "csv_import",
                "discovered_at": datetime.now().isoformat(),
                "status": "prospect"
            }
            prospects.append(prospect)
    
    # Save to prospects.json
    save_prospects(prospects)
    print(f"✅ Imported {len(prospects)} prospects from {filepath}")


def import_from_linkedin_urls(urls_file: str, niche: str = "saas"):
    """Import prospects from a text file of LinkedIn URLs."""
    prospects = []
    
    with open(urls_file, 'r') as f:
        for line in f:
            url = line.strip()
            if not url or not url.startswith('https://www.linkedin.com/'):
                continue
            
            # Extract name from URL if possible
            parts = url.split('/in/')
            if len(parts) > 1:
                slug = parts[1].split('/')[0].split('?')[0]
                name = slug.replace('-', ' ').title()
            else:
                name = "Unknown"
            
            prospect = {
                "prospect_id": f"li_{hash(url) % 1000000}",
                "name": name,
                "title": "",
                "company": "",
                "linkedin_url": url,
                "niche": niche,
                "source": "linkedin_url_list",
                "discovered_at": datetime.now().isoformat(),
                "status": "prospect"
            }
            prospects.append(prospect)
    
    save_prospects(prospects)
    print(f"✅ Imported {len(prospects)} LinkedIn URLs from {urls_file}")


def export_to_csv(filepath: str, stage_filter: str = None):
    """Export prospects to CSV."""
    prospects_file = Path('data/prospects.json')
    
    if not prospects_file.exists():
        print("❌ No prospects found")
        return
    
    with open(prospects_file) as f:
        all_prospects = json.load(f)
    
    # Filter if needed
    if stage_filter:
        prospects = [
            p for p in all_prospects.values()
            if p.get('stage') == stage_filter
        ]
    else:
        prospects = list(all_prospects.values())
    
    if not prospects:
        print(f"❌ No prospects found with filter: {stage_filter}")
        return
    
    # Write CSV
    with open(filepath, 'w', newline='') as f:
        if prospects:
            writer = csv.DictWriter(f, fieldnames=prospects[0].keys())
            writer.writeheader()
            writer.writerows(prospects)
    
    print(f"✅ Exported {len(prospects)} prospects to {filepath}")


def export_qualified_leads(filepath: str = "qualified_leads.csv"):
    """Export qualified leads for sales follow-up."""
    export_to_csv(filepath, stage_filter="qualified")


def save_prospects(prospects: list):
    """Save prospects to the main prospects.json file."""
    prospects_file = Path('data/prospects.json')
    
    # Load existing
    if prospects_file.exists():
        with open(prospects_file) as f:
            existing = json.load(f)
    else:
        existing = {}
    
    # Add new prospects
    for p in prospects:
        existing[p['prospect_id']] = p
    
    # Save
    with open(prospects_file, 'w') as f:
        json.dump(existing, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Import/Export prospects')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Import CSV
    import_csv = subparsers.add_parser('import-csv', help='Import from CSV')
    import_csv.add_argument('filepath', help='Path to CSV file')
    import_csv.add_argument('--niche', default='saas', choices=['saas', 'agency'])
    
    # Import LinkedIn URLs
    import_li = subparsers.add_parser('import-linkedin', help='Import from LinkedIn URLs file')
    import_li.add_argument('filepath', help='Path to text file with LinkedIn URLs')
    import_li.add_argument('--niche', default='saas', choices=['saas', 'agency'])
    
    # Export
    export = subparsers.add_parser('export', help='Export to CSV')
    export.add_argument('filepath', help='Output CSV file path')
    export.add_argument('--stage', help='Filter by stage')
    
    # Export qualified
    subparsers.add_parser('export-qualified', help='Export qualified leads')
    
    args = parser.parse_args()
    
    if args.command == 'import-csv':
        import_from_csv(args.filepath, args.niche)
    elif args.command == 'import-linkedin':
        import_from_linkedin_urls(args.filepath, args.niche)
    elif args.command == 'export':
        export_to_csv(args.filepath, args.stage)
    elif args.command == 'export-qualified':
        export_qualified_leads()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
