"""
Simple Web Dashboard
Monitor the Kimi Agent System from a browser
"""
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP handler for dashboard requests."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/' or path == '/dashboard':
            self._serve_dashboard()
        elif path == '/api/stats':
            self._serve_api_stats()
        elif path == '/api/pipeline':
            self._serve_api_pipeline()
        elif path == '/api/reports':
            self._serve_api_reports()
        else:
            self._serve_404()
    
    def _serve_dashboard(self):
        """Serve the HTML dashboard."""
        html = self._generate_html()
        self._send_response(200, 'text/html', html)
    
    def _serve_api_stats(self):
        """Serve JSON stats API."""
        stats = self._get_system_stats()
        self._send_response(200, 'application/json', json.dumps(stats, indent=2))
    
    def _serve_api_pipeline(self):
        """Serve JSON pipeline API."""
        pipeline = self._get_pipeline_data()
        self._send_response(200, 'application/json', json.dumps(pipeline, indent=2))
    
    def _serve_api_reports(self):
        """Serve recent reports."""
        reports = self._get_recent_reports()
        self._send_response(200, 'application/json', json.dumps(reports, indent=2))
    
    def _serve_404(self):
        """Serve 404 error."""
        self._send_response(404, 'text/plain', 'Not Found')
    
    def _send_response(self, status, content_type, body):
        """Send HTTP response."""
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body.encode() if isinstance(body, str) else body)
    
    def _get_system_stats(self):
        """Get current system statistics."""
        stats = {
            "timestamp": datetime.now().isoformat(),
            "prospects": 0,
            "pipeline_value": 0,
            "deals_won": 0,
            "daily_connections": 0,
            "today_tasks": 0
        }
        
        # Load prospects
        prospects_file = Path('data/prospects.json')
        if prospects_file.exists():
            with open(prospects_file) as f:
                prospects = json.load(f)
                stats['prospects'] = len(prospects)
                
                # Calculate pipeline value
                deal_values = {
                    'discovery_call_booked': 8000,
                    'proposal_sent': 10000,
                    'negotiation': 10000,
                    'closed_won': 10000
                }
                
                for p in prospects.values():
                    stage = p.get('stage', '')
                    if stage in deal_values:
                        stats['pipeline_value'] += deal_values[stage]
                    if stage == 'closed_won':
                        stats['deals_won'] += 1
        
        # Load tasks
        tasks_file = Path('data/tasks.json')
        if tasks_file.exists():
            with open(tasks_file) as f:
                tasks = json.load(f)
                today = datetime.now().strftime('%Y-%m-%d')
                stats['today_tasks'] = sum(
                    1 for t in tasks 
                    if t.get('due_date', '').startswith(today) and t.get('status') == 'pending'
                )
        
        return stats
    
    def _get_pipeline_data(self):
        """Get pipeline stage breakdown."""
        stages = {}
        
        prospects_file = Path('data/prospects.json')
        if prospects_file.exists():
            with open(prospects_file) as f:
                prospects = json.load(f)
                for p in prospects.values():
                    stage = p.get('stage', 'unknown')
                    stages[stage] = stages.get(stage, 0) + 1
        
        return {
            "stages": stages,
            "total": sum(stages.values())
        }
    
    def _get_recent_reports(self, days=7):
        """Get recent daily reports."""
        reports = []
        reports_dir = Path('data/daily_reports')
        
        if reports_dir.exists():
            for report_file in sorted(reports_dir.glob('report_*.json'), reverse=True)[:days]:
                with open(report_file) as f:
                    data = json.load(f)
                    reports.append({
                        "date": data.get('date'),
                        "new_prospects": data.get('data', {}).get('final_actions', 0),
                        "pipeline_value": data.get('pipeline', {}).get('pipeline_value', 0)
                    })
        
        return reports
    
    def _generate_html(self):
        """Generate dashboard HTML."""
        stats = self._get_system_stats()
        pipeline = self._get_pipeline_data()
        reports = self._get_recent_reports()
        
        stage_colors = {
            'prospect': '#3498db',
            'outreach': '#9b59b6',
            'connected': '#1abc9c',
            'engaged': '#f1c40f',
            'qualified': '#e67e22',
            'discovery_call_booked': '#e74c3c',
            'proposal_sent': '#c0392b',
            'negotiation': '#d35400',
            'closed_won': '#27ae60',
            'closed_lost': '#95a5a6'
        }
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Kimi Agent Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f6fa;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #2c3e50;
            font-size: 28px;
            margin-bottom: 5px;
        }}
        .header p {{
            color: #7f8c8d;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .stat-card h3 {{
            font-size: 12px;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        .stat-card .value {{
            font-size: 32px;
            font-weight: 700;
            color: #2c3e50;
        }}
        .stat-card .positive {{
            color: #27ae60;
        }}
        .section {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            font-size: 18px;
            color: #2c3e50;
            margin-bottom: 15px;
        }}
        .pipeline-bar {{
            display: flex;
            height: 40px;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 15px;
        }}
        .pipeline-segment {{
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            font-weight: 600;
            min-width: 40px;
            transition: all 0.3s;
        }}
        .pipeline-segment:hover {{
            opacity: 0.8;
        }}
        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 13px;
            color: #7f8c8d;
        }}
        .legend-color {{
            width: 12px;
            height: 12px;
            border-radius: 3px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }}
        th {{
            font-size: 12px;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .timestamp {{
            text-align: center;
            color: #95a5a6;
            font-size: 12px;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Kimi K2.5 Agent System</h1>
        <p>90-Day Revenue Target: $15K-$30K</p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <h3>Total Prospects</h3>
            <div class="value">{stats['prospects']}</div>
        </div>
        <div class="stat-card">
            <h3>Pipeline Value</h3>
            <div class="value">${stats['pipeline_value']:,}</div>
        </div>
        <div class="stat-card">
            <h3>Deals Closed</h3>
            <div class="value positive">{stats['deals_won']}</div>
        </div>
        <div class="stat-card">
            <h3>Today's Tasks</h3>
            <div class="value">{stats['today_tasks']}</div>
        </div>
    </div>
    
    <div class="section">
        <h2>📊 Pipeline Overview</h2>
        <div class="pipeline-bar">
"""
        
        # Add pipeline segments
        total = pipeline['total'] or 1  # Avoid division by zero
        for stage, count in pipeline['stages'].items():
            width = (count / total) * 100
            color = stage_colors.get(stage, '#3498db')
            html += f'            <div class="pipeline-segment" style="width: {width:.1f}%; background: {color};">{count}</div>\n'
        
        html += """        </div>
        <div class="legend">
"""
        
        # Add legend
        for stage, count in pipeline['stages'].items():
            color = stage_colors.get(stage, '#3498db')
            html += f'            <div class="legend-item"><div class="legend-color" style="background: {color};"></div>{stage.replace("_", " ").title()}: {count}</div>\n'
        
        html += """        </div>
    </div>
    
    <div class="section">
        <h2>📈 Recent Activity</h2>
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Actions</th>
                    <th>Pipeline Value</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # Add report rows
        for report in reports:
            html += f"""                <tr>
                    <td>{report['date']}</td>
                    <td>{report['new_prospects']}</td>
                    <td>${report['pipeline_value']:,}</td>
                </tr>
"""
        
        html += f"""            </tbody>
        </table>
    </div>
    
    <div class="timestamp">
        Last updated: {stats['timestamp'][:19].replace('T', ' ')}
    </div>
    
    <script>
        // Auto-refresh every 60 seconds
        setTimeout(() => window.location.reload(), 60000);
    </script>
</body>
</html>
"""
        return html


def run_server(port=8080):
    """Run the dashboard server."""
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    logger.info(f"🌐 Dashboard running at http://localhost:{port}")
    logger.info("Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n🛑 Server stopped")
        server.shutdown()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    
    run_server(args.port)
