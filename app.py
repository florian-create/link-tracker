from flask import Flask, request, jsonify, redirect, render_template_string, session, url_for
from flask_cors import CORS
from functools import wraps
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
import secrets
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app)

# Session configuration
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True  # Enable in production with HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Authorized users
AUTHORIZED_USERS = {
    'olivier@aura.camp': 'aura742446@',
    'florian@aura.camp': 'aura742446@'
}

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost/link_tracker')

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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
            company_name VARCHAR(255),
            company_url TEXT,
            linkedin_url TEXT,
            destination_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sent_to_clay BOOLEAN DEFAULT FALSE,
            sent_to_clay_at TIMESTAMP
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email in AUTHORIZED_USERS and AUTHORIZED_USERS[email] == password:
            session['user'] = email
            return redirect(url_for('index'))
        else:
            return render_template_string(LOGIN_HTML, error="Identifiants incorrects")

    return render_template_string(LOGIN_HTML)

@app.route('/logout')
def logout():
    """Logout"""
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Dashboard homepage"""
    try:
        with open('dashboard_corporate.html', 'r') as f:
            dashboard_html = f.read()
            # Add logout button to dashboard
            logout_button = '''
            <style>
                .logout-btn {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 0.75rem 1.5rem;
                    background: rgba(255, 255, 255, 0.2);
                    color: white;
                    border: 2px solid white;
                    border-radius: 8px;
                    font-weight: 600;
                    cursor: pointer;
                    text-decoration: none;
                    transition: all 0.2s;
                    z-index: 1000;
                }
                .logout-btn:hover {
                    background: white;
                    color: #667eea;
                }
                .user-info {
                    position: fixed;
                    top: 80px;
                    right: 20px;
                    padding: 0.5rem 1rem;
                    background: rgba(255, 255, 255, 0.95);
                    color: #667eea;
                    border-radius: 8px;
                    font-size: 0.875rem;
                    font-weight: 600;
                    z-index: 1000;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }
            </style>
            <a href="/logout" class="logout-btn">Déconnexion</a>
            <div class="user-info">👤 ''' + session.get('user', '') + '''</div>
            '''
            dashboard_html = dashboard_html.replace('</head>', logout_button + '</head>')
            return dashboard_html
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
    company_name = data.get('company_name', '')
    company_url = data.get('company_url', '')
    linkedin_url = data.get('linkedin_url', '')
    destination_url = data.get('destination_url')

    # Generate unique link ID
    link_id = generate_short_id()

    # Store in database
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute('''
            INSERT INTO links (link_id, first_name, last_name, email, icp, campaign, company_name, company_url, linkedin_url, destination_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (link_id, first_name, last_name, email, icp, campaign, company_name, company_url, linkedin_url, destination_url))

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
    """Get detailed click data with person info - with pagination and filtering"""
    campaign = request.args.get('campaign', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    search = request.args.get('search', '')
    status_filter = request.args.get('status', 'all')  # all, clicked, not_clicked

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Base query
    query = '''
        SELECT
            l.link_id,
            l.first_name,
            l.last_name,
            l.email,
            l.icp,
            l.campaign,
            l.company_name,
            l.company_url,
            l.linkedin_url,
            l.created_at,
            COUNT(c.id) as click_count,
            MAX(c.clicked_at) as last_clicked,
            MIN(c.clicked_at) as first_clicked
        FROM links l
        LEFT JOIN clicks c ON l.link_id = c.link_id
    '''

    # Count query for pagination
    count_query = '''
        SELECT COUNT(DISTINCT l.link_id) as total
        FROM links l
        LEFT JOIN clicks c ON l.link_id = c.link_id
    '''

    # Build WHERE conditions
    conditions = []
    params = []

    if campaign:
        conditions.append('l.campaign = %s')
        params.append(campaign)

    if search:
        search_condition = "(l.first_name ILIKE %s OR l.last_name ILIKE %s OR l.email ILIKE %s)"
        conditions.append(search_condition)
        search_param = f'%{search}%'
        params.extend([search_param, search_param, search_param])

    where_clause = ''
    if conditions:
        where_clause = ' WHERE ' + ' AND '.join(conditions)

    # Add WHERE clause to both queries
    query += where_clause
    count_query += where_clause

    # Group by for main query
    query += ' GROUP BY l.link_id, l.first_name, l.last_name, l.email, l.icp, l.campaign, l.company_name, l.company_url, l.linkedin_url, l.created_at'

    # Apply status filter after GROUP BY using HAVING
    if status_filter == 'clicked':
        query += ' HAVING COUNT(c.id) > 0'
    elif status_filter == 'not_clicked':
        query += ' HAVING COUNT(c.id) = 0'

    # Get total count
    cur.execute(count_query, params)
    total = cur.fetchone()['total']

    # Apply status filter to count if needed
    if status_filter == 'clicked':
        count_filtered = '''
            SELECT COUNT(*) as total FROM (
                SELECT l.link_id
                FROM links l
                LEFT JOIN clicks c ON l.link_id = c.link_id
                {where}
                GROUP BY l.link_id
                HAVING COUNT(c.id) > 0
            ) as filtered
        '''.format(where=where_clause)
        cur.execute(count_filtered, params)
        total = cur.fetchone()['total']
    elif status_filter == 'not_clicked':
        count_filtered = '''
            SELECT COUNT(*) as total FROM (
                SELECT l.link_id
                FROM links l
                LEFT JOIN clicks c ON l.link_id = c.link_id
                {where}
                GROUP BY l.link_id
                HAVING COUNT(c.id) = 0
            ) as filtered
        '''.format(where=where_clause)
        cur.execute(count_filtered, params)
        total = cur.fetchone()['total']

    # Add ordering and pagination
    query += ' ORDER BY click_count DESC, l.created_at DESC'
    offset = (page - 1) * per_page
    query += f' LIMIT {per_page} OFFSET {offset}'

    # Execute main query
    cur.execute(query, params)
    clicks = cur.fetchall()

    cur.close()
    conn.close()

    # Calculate pagination metadata
    total_pages = (total + per_page - 1) // per_page  # Ceiling division

    return jsonify({
        'data': clicks,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    })

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

    # Build WHERE clause combining campaign and time filters
    where_conditions = []
    if campaign_filter:
        where_conditions.append(f"l.campaign = '{campaign_filter}'")

    # Add time filter to the CTE to only get first clicks within the period
    if time_range == '24h':
        where_conditions.append("c.clicked_at >= NOW() - INTERVAL '24 hours'")
    elif time_range == '7d':
        where_conditions.append("c.clicked_at >= NOW() - INTERVAL '7 days'")
    elif time_range == '30d':
        where_conditions.append("c.clicked_at >= NOW() - INTERVAL '30 days'")

    where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

    # Get first click per unique visitor (by link_id = unique person) within the time period
    query = f'''
        WITH first_clicks AS (
            SELECT DISTINCT ON (c.link_id)
                c.clicked_at
            FROM clicks c
            JOIN links l ON c.link_id = l.link_id
            {where_clause}
            ORDER BY c.link_id, c.clicked_at ASC
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

    # Build WHERE clause for filtering first clicks within the time period
    where_conditions = [f"c.clicked_at >= NOW() - INTERVAL '{start_interval}'"]
    if campaign_filter:
        where_conditions.append(f"l.campaign = '{campaign_filter}'")

    where_clause = "WHERE " + " AND ".join(where_conditions)

    # Get first click per unique visitor (by link_id) within the time period
    # AND get total clicks count
    query = f'''
        WITH time_series AS (
            SELECT generate_series(
                NOW() - INTERVAL '{start_interval}',
                NOW(),
                INTERVAL '{step_interval}'
            ) AS period_time
        ),
        first_clicks AS (
            SELECT DISTINCT ON (c.link_id)
                c.link_id,
                c.clicked_at
            FROM clicks c
            JOIN links l ON c.link_id = l.link_id
            {where_clause}
            ORDER BY c.link_id, c.clicked_at ASC
        ),
        all_clicks AS (
            SELECT
                c.clicked_at
            FROM clicks c
            JOIN links l ON c.link_id = l.link_id
            {where_clause}
        )
        SELECT
            TO_CHAR(ts.period_time, '{format_str}') as period,
            COALESCE(COUNT(DISTINCT fc.link_id), 0) as unique_visitors,
            COALESCE(
                (SELECT COUNT(*)
                 FROM all_clicks ac
                 WHERE TO_CHAR(ac.clicked_at, '{format_str}') = TO_CHAR(ts.period_time, '{format_str}')
                ), 0
            ) as total_clicks
        FROM time_series ts
        LEFT JOIN first_clicks fc
            ON TO_CHAR(fc.clicked_at, '{format_str}') = TO_CHAR(ts.period_time, '{format_str}')
        GROUP BY period, ts.period_time
        ORDER BY ts.period_time
    '''

    cur.execute(query)
    timeline_data = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(timeline_data)

@app.route('/api/update-link', methods=['POST', 'PUT'])
def update_link():
    """Update an existing link with new company and LinkedIn information"""
    data = request.json

    # Need at least one identifier to find the link
    email = data.get('email')
    link_id = data.get('link_id')

    if not email and not link_id:
        return jsonify({'error': 'email or link_id is required to identify the link'}), 400

    # Get the fields to update
    company_name = data.get('company_name')
    company_url = data.get('company_url')
    linkedin_url = data.get('linkedin_url')

    # Build update query dynamically based on provided fields
    update_fields = []
    params = []

    if company_name is not None:
        update_fields.append('company_name = %s')
        params.append(company_name)

    if company_url is not None:
        update_fields.append('company_url = %s')
        params.append(company_url)

    if linkedin_url is not None:
        update_fields.append('linkedin_url = %s')
        params.append(linkedin_url)

    if not update_fields:
        return jsonify({'error': 'No fields to update. Provide company_name, company_url, or linkedin_url'}), 400

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Build WHERE clause
        where_clause = 'link_id = %s' if link_id else 'email = %s'
        identifier = link_id if link_id else email
        params.append(identifier)

        # Execute update
        query = f"UPDATE links SET {', '.join(update_fields)} WHERE {where_clause}"
        cur.execute(query, params)

        conn.commit()

        if cur.rowcount == 0:
            return jsonify({'error': 'Link not found', 'searched_by': 'link_id' if link_id else 'email', 'value': identifier}), 404

        # Return updated link info
        cur.execute('SELECT * FROM links WHERE ' + where_clause, (identifier,))
        updated_link = cur.fetchone()

        return jsonify({
            'success': True,
            'message': f'Updated {cur.rowcount} link(s)',
            'link': updated_link
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

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

@app.route('/api/webhook/hot-leads', methods=['POST', 'GET'])
def send_hot_leads_to_clay():
    """Send leads with 5+ clicks to Clay webhook - Manual or automated trigger"""

    # Get Clay webhook URL from request or environment
    data = request.json if request.method == 'POST' else {}
    clay_webhook_url = data.get('clay_webhook_url') or os.environ.get('CLAY_WEBHOOK_URL')

    if not clay_webhook_url:
        return jsonify({'error': 'clay_webhook_url is required. Provide it in the request body or set CLAY_WEBHOOK_URL environment variable'}), 400

    # Get optional parameters
    min_clicks = int(data.get('min_clicks', 5))  # Default: 5 clicks
    campaign_filter = data.get('campaign', '')

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Find hot leads: 5+ clicks AND not yet sent to Clay
        query = '''
            SELECT
                l.link_id,
                l.first_name,
                l.last_name,
                l.email,
                l.icp,
                l.campaign,
                l.company_name,
                l.company_url,
                l.linkedin_url,
                l.destination_url,
                l.created_at,
                COUNT(c.id) as click_count,
                MAX(c.clicked_at) as last_clicked,
                MIN(c.clicked_at) as first_clicked
            FROM links l
            LEFT JOIN clicks c ON l.link_id = c.link_id
            WHERE l.sent_to_clay = FALSE
        '''

        if campaign_filter:
            query += f" AND l.campaign = '{campaign_filter}'"

        query += f'''
            GROUP BY l.link_id, l.first_name, l.last_name, l.email, l.icp, l.campaign,
                     l.company_name, l.company_url, l.linkedin_url, l.destination_url, l.created_at
            HAVING COUNT(c.id) >= {min_clicks}
            ORDER BY COUNT(c.id) DESC
        '''

        cur.execute(query)
        hot_leads = cur.fetchall()

        if not hot_leads:
            return jsonify({
                'success': True,
                'message': 'No hot leads found',
                'sent_count': 0,
                'min_clicks': min_clicks
            }), 200

        # Send each lead to Clay webhook
        sent_count = 0
        errors = []
        sent_link_ids = []

        for lead in hot_leads:
            try:
                # Prepare payload for Clay
                payload = {
                    'first_name': lead['first_name'],
                    'last_name': lead['last_name'],
                    'email': lead['email'],
                    'company_name': lead['company_name'],
                    'company_url': lead['company_url'],
                    'linkedin_url': lead['linkedin_url'],
                    'icp': lead['icp'],
                    'campaign': lead['campaign'],
                    'click_count': lead['click_count'],
                    'first_clicked': lead['first_clicked'].isoformat() if lead['first_clicked'] else None,
                    'last_clicked': lead['last_clicked'].isoformat() if lead['last_clicked'] else None,
                    'link_id': lead['link_id'],
                    'tracking_url': f"https://{os.getenv('CUSTOM_DOMAIN', 'link-tracker.onrender.com')}/c/{lead['link_id']}"
                }

                # Send to Clay webhook
                response = requests.post(clay_webhook_url, json=payload, timeout=10)

                if response.status_code in [200, 201, 202]:
                    sent_count += 1
                    sent_link_ids.append(lead['link_id'])
                else:
                    errors.append({
                        'email': lead['email'],
                        'error': f"Clay webhook returned {response.status_code}"
                    })

            except Exception as e:
                errors.append({
                    'email': lead['email'],
                    'error': str(e)
                })

        # Mark sent leads as sent_to_clay
        if sent_link_ids:
            placeholders = ','.join(['%s'] * len(sent_link_ids))
            cur.execute(f'''
                UPDATE links
                SET sent_to_clay = TRUE, sent_to_clay_at = NOW()
                WHERE link_id IN ({placeholders})
            ''', sent_link_ids)
            conn.commit()

        return jsonify({
            'success': True,
            'message': f'Sent {sent_count} hot leads to Clay',
            'sent_count': sent_count,
            'total_found': len(hot_leads),
            'min_clicks': min_clicks,
            'errors': errors if errors else None
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/webhook/reset-clay-status', methods=['POST'])
def reset_clay_status():
    """Reset sent_to_clay status for testing purposes"""
    data = request.json or {}
    email = data.get('email')

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if email:
            cur.execute('UPDATE links SET sent_to_clay = FALSE, sent_to_clay_at = NULL WHERE email = %s', (email,))
        else:
            cur.execute('UPDATE links SET sent_to_clay = FALSE, sent_to_clay_at = NULL')

        conn.commit()
        count = cur.rowcount

        return jsonify({
            'success': True,
            'message': f'Reset {count} link(s)',
            'count': count
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# Login HTML Template
LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Link Tracker</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1rem;
        }

        .login-container {
            background: white;
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 400px;
        }

        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }

        .login-header h1 {
            font-size: 2rem;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }

        .login-header p {
            color: #718096;
            font-size: 0.95rem;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-group label {
            display: block;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 0.5rem;
            font-size: 0.875rem;
        }

        .form-group input {
            width: 100%;
            padding: 0.875rem 1rem;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 1rem;
            transition: all 0.2s;
            outline: none;
        }

        .form-group input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .login-btn {
            width: 100%;
            padding: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-top: 1rem;
        }

        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        .login-btn:active {
            transform: translateY(0);
        }

        .error-message {
            background: #fed7d7;
            color: #c53030;
            padding: 0.875rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            font-size: 0.875rem;
            text-align: center;
            font-weight: 600;
        }

        .logo {
            font-size: 3rem;
            margin-bottom: 1rem;
        }

        @media (max-width: 480px) {
            .login-container {
                padding: 2rem 1.5rem;
            }

            .login-header h1 {
                font-size: 1.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <div class="logo">🔐</div>
            <h1>Link Tracker</h1>
            <p>Connectez-vous pour accéder au dashboard</p>
        </div>

        {% if error %}
        <div class="error-message">
            {{ error }}
        </div>
        {% endif %}

        <form method="POST" action="/login">
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" placeholder="olivier@aura.camp" required autofocus>
            </div>

            <div class="form-group">
                <label for="password">Mot de passe</label>
                <input type="password" id="password" name="password" placeholder="Entrez votre mot de passe" required>
            </div>

            <button type="submit" class="login-btn">Se connecter</button>
        </form>
    </div>
</body>
</html>
'''

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
