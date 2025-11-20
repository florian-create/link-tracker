from flask import Flask, request, jsonify, redirect, render_template_string
from flask_cors import CORS
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
import secrets
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app)

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost/link_tracker')

def get_db_connection():
    """Create database connection"""
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def ensure_tables_exist():
    """Ensure database tables exist, create them if they don't"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if tables exist
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'links'
            )
        """)

        if not cur.fetchone()[0]:
            # Tables don't exist, create them
            init_db()

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error checking/creating tables: {e}")

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    cur = conn.cursor()

    # Links table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id SERIAL PRIMARY KEY,
            link_id VARCHAR(10) UNIQUE NOT NULL,
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            email VARCHAR(255),
            icp VARCHAR(255),
            campaign VARCHAR(255),
            destination_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Clicks table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            id SERIAL PRIMARY KEY,
            link_id VARCHAR(10) NOT NULL,
            clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(45),
            user_agent TEXT,
            country VARCHAR(100),
            city VARCHAR(100),
            referer TEXT,
            FOREIGN KEY (link_id) REFERENCES links(link_id)
        )
    ''')

    conn.commit()
    cur.close()
    conn.close()

def generate_short_id():
    """Generate a unique short ID for links"""
    return secrets.token_urlsafe(6)[:8]

def get_geo_info(ip):
    """Get geolocation info from IP address"""
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}', timeout=2)
        if response.status_code == 200:
            data = response.json()
            return data.get('country', 'Unknown'), data.get('city', 'Unknown')
    except:
        pass
    return 'Unknown', 'Unknown'

@app.route('/')
def index():
    """Dashboard homepage"""
    try:
        with open('dashboard_corporate.html', 'r') as f:
            return f.read()
    except:
        return render_template_string(DASHBOARD_HTML)

@app.route('/api/version')
def get_version():
    """Get API version to verify deployment"""
    return jsonify({
        'version': '2.0-unique-visitors',
        'heatmap': 'Uses DISTINCT ON ip_address for unique visitors',
        'timeline': 'Uses DISTINCT ON ip_address for unique visitors',
        'deployed_at': datetime.now().isoformat()
    })

@app.route('/api/create-link', methods=['POST'])
def create_link():
    """Create a new tracked link - Called from Clay"""
    # Ensure tables exist on first request
    ensure_tables_exist()

    data = request.json

    # Validate required fields
    if not data.get('destination_url'):
        return jsonify({'error': 'destination_url is required'}), 400

    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    email = data.get('email', '')
    icp = data.get('ICP', data.get('icp', ''))  # Support both ICP and icp
    campaign = data.get('campaign', 'default')
    destination_url = data.get('destination_url')

    # Generate unique link ID
    link_id = generate_short_id()

    # Store in database
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute('''
            INSERT INTO links (link_id, first_name, last_name, email, icp, campaign, destination_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (link_id, first_name, last_name, email, icp, campaign, destination_url))

        conn.commit()

        # Determine domain based on campaign
        # Support for multiple custom domains via environment variables
        if 'wesser' in campaign.lower():
            # Use Wesser custom domain
            custom_domain = os.getenv('WESSER_DOMAIN', os.getenv('CUSTOM_DOMAIN', 'link-tracker.onrender.com'))
        elif 'aura' in campaign.lower():
            # Use Aura custom domain
            custom_domain = os.getenv('AURA_DOMAIN', os.getenv('CUSTOM_DOMAIN', 'agence.aura.camp'))
        else:
            # Default domain
            custom_domain = os.getenv('CUSTOM_DOMAIN', 'link-tracker.onrender.com')

        base_url = f"https://{custom_domain}"
        short_url = f"{base_url}/c/{link_id}"

        return jsonify({
            'success': True,
            'short_url': short_url,
            'link_id': link_id
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/c/<link_id>')
def redirect_link(link_id):
    """Redirect short link and track the click"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Get link info
    cur.execute('SELECT * FROM links WHERE link_id = %s', (link_id,))
    link = cur.fetchone()

    if not link:
        cur.close()
        conn.close()
        return "Link not found", 404

    # Track the click
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', '')
    referer = request.headers.get('Referer', '')

    # Get geolocation
    country, city = get_geo_info(ip_address)

    cur.execute('''
        INSERT INTO clicks (link_id, ip_address, user_agent, country, city, referer)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (link_id, ip_address, user_agent, country, city, referer))

    conn.commit()
    cur.close()
    conn.close()

    # Redirect to destination
    return redirect(link['destination_url'])

@app.route('/api/analytics')
def get_analytics():
    """Get overall analytics with time range and campaign filter"""
    time_range = request.args.get('range', 'all')  # 24h, 7d, 30d, all
    campaign_filter = request.args.get('campaign', '')

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Build time filter for clicks
    time_filter = ""
    if time_range == '24h':
        time_filter = "WHERE c.clicked_at >= NOW() - INTERVAL '24 hours'"
    elif time_range == '7d':
        time_filter = "WHERE c.clicked_at >= NOW() - INTERVAL '7 days'"
    elif time_range == '30d':
        time_filter = "WHERE c.clicked_at >= NOW() - INTERVAL '30 days'"

    # Add campaign filter
    if campaign_filter:
        if time_filter:
            time_filter += f" AND l.campaign = '{campaign_filter}'"
        else:
            time_filter = f"WHERE l.campaign = '{campaign_filter}'"

    # Total links created (with campaign filter)
    if campaign_filter:
        cur.execute(f"SELECT COUNT(*) as total_links FROM links WHERE campaign = '{campaign_filter}'")
    else:
        cur.execute('SELECT COUNT(*) as total_links FROM links')
    total_links = cur.fetchone()['total_links']

    # Total clicks (with time and campaign filter)
    if time_filter:
        cur.execute(f'SELECT COUNT(*) as total_clicks FROM clicks c JOIN links l ON c.link_id = l.link_id {time_filter}')
    else:
        cur.execute('SELECT COUNT(*) as total_clicks FROM clicks')
    total_clicks = cur.fetchone()['total_clicks']

    # Unique links clicked (with time and campaign filter)
    if time_filter:
        cur.execute(f'SELECT COUNT(DISTINCT c.link_id) as unique_clicks FROM clicks c JOIN links l ON c.link_id = l.link_id {time_filter}')
    else:
        cur.execute('SELECT COUNT(DISTINCT link_id) as unique_clicks FROM clicks')
    unique_clicks = cur.fetchone()['unique_clicks']

    # Click rate
    click_rate = (unique_clicks / total_links * 100) if total_links > 0 else 0

    # Clicks by campaign (with time filter) - need to adjust time_filter for this query
    campaign_time_filter = time_filter.replace('WHERE c.', 'WHERE ').replace('c.clicked_at', 'c.clicked_at') if time_filter and 'WHERE c.' in time_filter else time_filter
    cur.execute(f'''
        SELECT l.campaign, COUNT(c.id) as clicks
        FROM links l
        LEFT JOIN clicks c ON l.link_id = c.link_id
        {campaign_time_filter}
        GROUP BY l.campaign
        ORDER BY clicks DESC
    ''')
    campaigns = cur.fetchall()

    # Recent clicks (with time filter)
    cur.execute(f'''
        SELECT l.first_name, l.last_name, l.email, l.campaign,
               c.clicked_at, c.country, c.city
        FROM clicks c
        JOIN links l ON c.link_id = l.link_id
        {time_filter}
        ORDER BY c.clicked_at DESC
        LIMIT 10
    ''')
    recent_clicks = cur.fetchall()

    # Top clickers (with time filter) - people who clicked the most
    top_clickers_query = '''
        SELECT
            l.first_name,
            l.last_name,
            l.email,
            COUNT(c.id) as clicks
        FROM clicks c
        JOIN links l ON c.link_id = l.link_id
    '''
    if campaign_filter and time_filter:
        top_clickers_query += f" WHERE l.campaign = '{campaign_filter}' AND {time_filter.replace('WHERE ', '')}"
    elif campaign_filter:
        top_clickers_query += f" WHERE l.campaign = '{campaign_filter}'"
    elif time_filter:
        top_clickers_query += f" {time_filter}"

    top_clickers_query += '''
        GROUP BY l.first_name, l.last_name, l.email
        ORDER BY clicks DESC
        LIMIT 10
    '''

    cur.execute(top_clickers_query)
    geo_data = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({
        'total_links': total_links,
        'total_clicks': total_clicks,
        'unique_clicks': unique_clicks,
        'click_rate': round(click_rate, 2),
        'campaigns': campaigns,
        'recent_clicks': recent_clicks,
        'geo_data': geo_data
    })

@app.route('/api/clicks')
def get_clicks():
    """Get detailed click data with person info"""
    campaign = request.args.get('campaign', '')

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    query = '''
        SELECT
            l.link_id,
            l.first_name,
            l.last_name,
            l.email,
            l.icp,
            l.campaign,
            l.created_at,
            COUNT(c.id) as click_count,
            MAX(c.clicked_at) as last_clicked,
            MIN(c.clicked_at) as first_clicked
        FROM links l
        LEFT JOIN clicks c ON l.link_id = c.link_id
    '''

    if campaign:
        query += ' WHERE l.campaign = %s'
        cur.execute(query + ' GROUP BY l.link_id, l.first_name, l.last_name, l.email, l.icp, l.campaign, l.created_at ORDER BY click_count DESC', (campaign,))
    else:
        cur.execute(query + ' GROUP BY l.link_id, l.first_name, l.last_name, l.email, l.icp, l.campaign, l.created_at ORDER BY click_count DESC')

    clicks = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(clicks)

@app.route('/api/campaigns')
def get_campaigns():
    """Get list of all campaigns"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute('SELECT DISTINCT campaign FROM links ORDER BY campaign')
    campaigns = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify([c['campaign'] for c in campaigns])

@app.route('/api/icp-stats')
def get_icp_stats():
    """Get ICP distribution for links that have been clicked"""
    time_range = request.args.get('range', 'all')
    campaign_filter = request.args.get('campaign', '')

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Build time filter for clicks
    time_filter = ""
    if time_range == '24h':
        time_filter = "AND c.clicked_at >= NOW() - INTERVAL '24 hours'"
    elif time_range == '7d':
        time_filter = "AND c.clicked_at >= NOW() - INTERVAL '7 days'"
    elif time_range == '30d':
        time_filter = "AND c.clicked_at >= NOW() - INTERVAL '30 days'"

    # Build campaign filter
    campaign_condition = ""
    if campaign_filter:
        campaign_condition = f"AND l.campaign = '{campaign_filter}'"

    # Get ICP distribution for clicked links only
    query = f'''
        SELECT
            COALESCE(NULLIF(l.icp, ''), 'Non défini') as icp,
            COUNT(DISTINCT l.link_id) as click_count
        FROM links l
        INNER JOIN clicks c ON l.link_id = c.link_id
        WHERE 1=1 {time_filter} {campaign_condition}
        GROUP BY l.icp
        ORDER BY click_count DESC
    '''

    cur.execute(query)
    icp_stats = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(icp_stats)

@app.route('/api/heatmap')
def get_heatmap():
    """Get click heatmap data by day of week and hour (unique visitors only)"""
    time_range = request.args.get('range', 'all')  # 24h, 7d, 30d, all
    campaign_filter = request.args.get('campaign', '')

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Build WHERE clause for first_clicks CTE
    where_conditions = []
    if time_range == '24h':
        where_conditions.append("c.clicked_at >= NOW() - INTERVAL '24 hours'")
    elif time_range == '7d':
        where_conditions.append("c.clicked_at >= NOW() - INTERVAL '7 days'")
    elif time_range == '30d':
        where_conditions.append("c.clicked_at >= NOW() - INTERVAL '30 days'")

    if campaign_filter:
        where_conditions.append(f"l.campaign = '{campaign_filter}'")

    where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

    # Count only the first click per unique visitor (ip_address)
    query = f'''
        WITH first_clicks AS (
            SELECT DISTINCT ON (c.ip_address)
                c.clicked_at
            FROM clicks c
            JOIN links l ON c.link_id = l.link_id
            {where_clause}
            ORDER BY c.ip_address, c.clicked_at ASC
        )
        SELECT
            EXTRACT(DOW FROM fc.clicked_at) as day_of_week,
            EXTRACT(HOUR FROM fc.clicked_at) as hour,
            COUNT(*) as click_count
        FROM first_clicks fc
        GROUP BY day_of_week, hour
        ORDER BY day_of_week, hour
    '''

    cur.execute(query)
    heatmap_data = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(heatmap_data)

@app.route('/api/analytics/timeline')
def get_timeline():
    """Get clicks timeline for chart (unique visitors only)"""
    time_range = request.args.get('range', '7d')
    campaign_filter = request.args.get('campaign', '')

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Configure based on time range
    if time_range == '24h':
        start_interval = '24 hours'
        step_interval = '1 hour'
        format_str = 'YYYY-MM-DD HH24:00'
    elif time_range == '7d':
        start_interval = '7 days'
        step_interval = '1 day'
        format_str = 'YYYY-MM-DD'
    elif time_range == '30d':
        start_interval = '30 days'
        step_interval = '1 day'
        format_str = 'YYYY-MM-DD'
    else:  # 'all'
        start_interval = '90 days'
        step_interval = '1 day'
        format_str = 'YYYY-MM-DD'

    # Build campaign join condition
    campaign_condition = ""
    if campaign_filter:
        campaign_condition = f"AND l.campaign = '{campaign_filter}'"

    # Generate all periods and LEFT JOIN with first clicks per unique visitor
    query = f'''
        WITH time_series AS (
            SELECT generate_series(
                NOW() - INTERVAL '{start_interval}',
                NOW(),
                INTERVAL '{step_interval}'
            ) AS period_time
        ),
        first_clicks AS (
            SELECT DISTINCT ON (c.ip_address)
                c.id,
                c.clicked_at,
                c.link_id
            FROM clicks c
            JOIN links l ON c.link_id = l.link_id
            WHERE c.clicked_at >= NOW() - INTERVAL '{start_interval}'
            {campaign_condition}
            ORDER BY c.ip_address, c.clicked_at ASC
        )
        SELECT
            TO_CHAR(ts.period_time, '{format_str}') as period,
            COALESCE(COUNT(fc.id), 0) as clicks
        FROM time_series ts
        LEFT JOIN first_clicks fc ON TO_CHAR(fc.clicked_at, '{format_str}') = TO_CHAR(ts.period_time, '{format_str}')
        GROUP BY period, ts.period_time
        ORDER BY ts.period_time
    '''

    cur.execute(query)
    timeline_data = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(timeline_data)

@app.route('/api/links/<link_id>', methods=['DELETE'])
def delete_link(link_id):
    """Delete a link and all its associated clicks"""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Delete clicks first (foreign key constraint)
        cur.execute('DELETE FROM clicks WHERE link_id = %s', (link_id,))

        # Then delete the link
        cur.execute('DELETE FROM links WHERE link_id = %s', (link_id,))

        conn.commit()

        if cur.rowcount == 0:
            return jsonify({'error': 'Link not found'}), 404

        return jsonify({'success': True, 'message': 'Link deleted'}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# Dashboard HTML Template
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Link Tracker Analytics</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f7fa;
            color: #2c3e50;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .header h1 {
            font-size: 2rem;
            font-weight: 600;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: transform 0.2s;
        }

        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        }

        .stat-label {
            font-size: 0.875rem;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }

        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #667eea;
        }

        .table-card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            overflow: hidden;
            margin-bottom: 2rem;
        }

        .table-header {
            padding: 1.5rem;
            border-bottom: 2px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .table-title {
            font-size: 1.25rem;
            font-weight: 600;
        }

        .filter-select {
            padding: 0.5rem 1rem;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 0.875rem;
            cursor: pointer;
            outline: none;
            transition: border-color 0.2s;
        }

        .filter-select:focus {
            border-color: #667eea;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        thead {
            background: #f7fafc;
        }

        th {
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            color: #4a5568;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        td {
            padding: 1rem;
            border-top: 1px solid #e2e8f0;
        }

        tbody tr:hover {
            background: #f7fafc;
        }

        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .badge-success {
            background: #c6f6d5;
            color: #22543d;
        }

        .badge-gray {
            background: #e2e8f0;
            color: #4a5568;
        }

        .badge-purple {
            background: #e9d8fd;
            color: #553c9a;
        }

        .export-btn {
            padding: 0.5rem 1.5rem;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }

        .export-btn:hover {
            background: #5568d3;
        }

        .loading {
            text-align: center;
            padding: 3rem;
            color: #718096;
        }

        .click-count {
            font-weight: 700;
            color: #667eea;
        }

        @media (max-width: 768px) {
            .stats-grid {
                grid-template-columns: 1fr;
            }

            table {
                font-size: 0.875rem;
            }

            th, td {
                padding: 0.75rem 0.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>📊 Link Tracker Analytics</h1>
        </div>
    </div>

    <div class="container">
        <div class="stats-grid" id="statsGrid">
            <div class="loading">Chargement des statistiques...</div>
        </div>

        <div class="table-card">
            <div class="table-header">
                <h2 class="table-title">Détails des clics par personne</h2>
                <div style="display: flex; gap: 1rem;">
                    <select class="filter-select" id="campaignFilter">
                        <option value="">Toutes les campagnes</option>
                    </select>
                    <button class="export-btn" onclick="exportCSV()">Export CSV</button>
                </div>
            </div>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th>Nom</th>
                            <th>Email</th>
                            <th>Campagne</th>
                            <th>Clics</th>
                            <th>Premier clic</th>
                            <th>Dernier clic</th>
                            <th>Statut</th>
                        </tr>
                    </thead>
                    <tbody id="clicksTable">
                        <tr><td colspan="7" class="loading">Chargement des données...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        let allClicks = [];

        // Load analytics on page load
        async function loadAnalytics() {
            try {
                const response = await fetch('/api/analytics');
                const data = await response.json();

                document.getElementById('statsGrid').innerHTML = `
                    <div class="stat-card">
                        <div class="stat-label">Total Liens</div>
                        <div class="stat-value">${data.total_links}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Total Clics</div>
                        <div class="stat-value">${data.total_clicks}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Personnes Uniques</div>
                        <div class="stat-value">${data.unique_clicks}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Taux d'ouverture</div>
                        <div class="stat-value">${data.click_rate}%</div>
                    </div>
                `;
            } catch (error) {
                console.error('Error loading analytics:', error);
            }
        }

        // Load clicks data
        async function loadClicks(campaign = '') {
            try {
                const url = campaign ? `/api/clicks?campaign=${campaign}` : '/api/clicks';
                const response = await fetch(url);
                allClicks = await response.json();

                renderClicksTable(allClicks);
            } catch (error) {
                console.error('Error loading clicks:', error);
            }
        }

        // Load campaigns for filter
        async function loadCampaigns() {
            try {
                const response = await fetch('/api/campaigns');
                const campaigns = await response.json();

                const select = document.getElementById('campaignFilter');
                campaigns.forEach(campaign => {
                    const option = document.createElement('option');
                    option.value = campaign;
                    option.textContent = campaign;
                    select.appendChild(option);
                });
            } catch (error) {
                console.error('Error loading campaigns:', error);
            }
        }

        // Render clicks table
        function renderClicksTable(clicks) {
            const tbody = document.getElementById('clicksTable');

            if (clicks.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="loading">Aucune donnée disponible</td></tr>';
                return;
            }

            tbody.innerHTML = clicks.map(click => `
                <tr>
                    <td><strong>${click.first_name} ${click.last_name}</strong></td>
                    <td>${click.email || '-'}</td>
                    <td><span class="badge badge-purple">${click.campaign}</span></td>
                    <td><span class="click-count">${click.click_count}</span></td>
                    <td>${click.first_clicked ? formatDate(click.first_clicked) : '-'}</td>
                    <td>${click.last_clicked ? formatDate(click.last_clicked) : '-'}</td>
                    <td>${click.click_count > 0 ? '<span class="badge badge-success">Cliqué</span>' : '<span class="badge badge-gray">Non cliqué</span>'}</td>
                </tr>
            `).join('');
        }

        // Format date
        function formatDate(dateString) {
            if (!dateString) return '-';
            const date = new Date(dateString);
            return date.toLocaleString('fr-FR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }

        // Export to CSV
        function exportCSV() {
            const headers = ['Prénom', 'Nom', 'Email', 'Campagne', 'Clics', 'Premier clic', 'Dernier clic', 'Statut'];
            const rows = allClicks.map(click => [
                click.first_name,
                click.last_name,
                click.email || '',
                click.campaign,
                click.click_count,
                click.first_clicked ? formatDate(click.first_clicked) : '',
                click.last_clicked ? formatDate(click.last_clicked) : '',
                click.click_count > 0 ? 'Cliqué' : 'Non cliqué'
            ]);

            const csv = [headers, ...rows].map(row => row.join(',')).join('\\n');
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `clicks_export_${Date.now()}.csv`;
            a.click();
        }

        // Event listeners
        document.getElementById('campaignFilter').addEventListener('change', (e) => {
            loadClicks(e.target.value);
        });

        // Initial load
        loadAnalytics();
        loadClicks();
        loadCampaigns();

        // Refresh every 30 seconds
        setInterval(() => {
            loadAnalytics();
            loadClicks(document.getElementById('campaignFilter').value);
        }, 30000);
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    # Initialize database on first run
    try:
        init_db()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Database initialization error: {e}")

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
