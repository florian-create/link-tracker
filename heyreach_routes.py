"""
HeyReach Exporter Routes
Routes pour l'export et l'analyse des conversations HeyReach
"""

from flask import render_template, request, jsonify, send_file, session, redirect, url_for, Blueprint
from werkzeug.security import check_password_hash, generate_password_hash
import requests
import io
import csv
from datetime import datetime
from functools import wraps
import os

# Create Blueprint
heyreach_bp = Blueprint('heyreach', __name__, url_prefix='/heyreach')

# Configuration
ADMIN_PASSWORD_HASH = os.environ.get('HEYREACH_PASSWORD_HASH', generate_password_hash('aura742446@'))

# Authentication decorator
def heyreach_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('heyreach_logged_in'):
            return redirect(url_for('heyreach.login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['logged_in'] = True
            session['username'] = request.form.get('username', 'User')
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Mot de passe incorrect")
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ===== HEYREACH API =====

class HeyReachAPI:
    """HeyReach API wrapper"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.heyreach.io/api/public"
        self.headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }

    def get_conversations(
        self,
        campaign_ids=None,
        linkedin_account_ids=None,
        date_from=None,
        date_to=None,
        offset=0,
        limit=100
    ):
        """Get conversations from HeyReach API"""
        url = f"{self.base_url}/inbox/GetConversationsV2"

        # Only add filters if they have actual values
        filters = {}
        if campaign_ids and len(campaign_ids) > 0:
            filters["campaignIds"] = campaign_ids
        if linkedin_account_ids and len(linkedin_account_ids) > 0:
            filters["linkedInAccountIds"] = linkedin_account_ids

        body = {
            "filters": filters,
            "offset": offset,
            "limit": limit
        }

        # Store date filters for client-side filtering (API doesn't support date filtering)
        self._date_from = date_from
        self._date_to = date_to

        print(f"=== API Request ===")
        print(f"URL: {url}")
        print(f"Body: {json.dumps(body, indent=2)}")
        print(f"Headers: X-API-KEY = {self.headers['X-API-KEY'][:20]}...")

        try:
            response = requests.post(url, headers=self.headers, json=body)
            print(f"Status Code: {response.status_code}")

            if response.status_code != 200:
                print(f"Error Response: {response.text}")
            else:
                print(f"Response: {response.text[:500]}...")

            response.raise_for_status()
            result = response.json()
            print(f"JSON Keys: {list(result.keys())}")
            return result
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            print(f"Response: {response.text if 'response' in locals() else 'No response'}")
            raise Exception(f"HeyReach API Error: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
            raise

    def get_all_conversations(self, campaign_ids=None, linkedin_account_ids=None, date_from=None, date_to=None):
        """Get all conversations with pagination using offset/limit"""
        all_conversations = []
        offset = 0
        limit = 100
        max_iterations = 1000  # Safety limit to prevent infinite loops

        print(f"=== Fetching ALL conversations (offset-based pagination) ===")
        if date_from or date_to:
            print(f"Date filter: {date_from} to {date_to}")

        for iteration in range(max_iterations):
            print(f"\n--- Fetching batch (offset={offset}, limit={limit}) ---")

            result = self.get_conversations(
                campaign_ids=campaign_ids,
                linkedin_account_ids=linkedin_account_ids,
                date_from=date_from,
                date_to=date_to,
                offset=offset,
                limit=limit
            )

            # HeyReach API returns conversations in "items" array
            conversations = result.get("items", [])
            total_count = result.get("totalCount", 0)

            print(f"✓ Fetched {len(conversations)} conversations (offset {offset})")
            print(f"✓ API totalCount: {total_count}")

            # If no conversations in this batch, we're done
            if not conversations or len(conversations) == 0:
                print(f"No more conversations. Stopping pagination.")
                if offset == 0:
                    print(f"Response structure: {list(result.keys())}")
                break

            all_conversations.extend(conversations)
            print(f"✓ Total fetched so far: {len(all_conversations)}/{total_count}")

            # Check if we've fetched all conversations
            if len(all_conversations) >= total_count:
                print(f"✓ All conversations fetched ({len(all_conversations)}/{total_count})")
                break

            # If we got less than limit items, we're done
            if len(conversations) < limit:
                print(f"✓ Last batch (got {len(conversations)} < {limit})")
                break

            # Move to next batch
            offset += limit
            print(f"→ Moving to next batch (new offset: {offset})")

        print(f"\n=== ✓ Total conversations fetched: {len(all_conversations)} ===")

        # Filter by date if specified (client-side filtering)
        if date_from or date_to:
            filtered_conversations = []
            for conv in all_conversations:
                last_msg_date = conv.get('lastMessageAt')
                if not last_msg_date:
                    continue

                try:
                    # Parse ISO 8601 datetime
                    from datetime import datetime
                    msg_date = datetime.fromisoformat(last_msg_date.replace('Z', '+00:00')).date()

                    # Check date range
                    if date_from:
                        from_date = datetime.fromisoformat(date_from).date()
                        if msg_date < from_date:
                            continue

                    if date_to:
                        to_date = datetime.fromisoformat(date_to).date()
                        if msg_date > to_date:
                            continue

                    filtered_conversations.append(conv)
                except Exception as e:
                    print(f"Error parsing date for conversation: {e}")
                    continue

            print(f"✓ Filtered by date: {len(filtered_conversations)}/{len(all_conversations)} conversations\n")
            return filtered_conversations

        return all_conversations

    def get_campaigns(self):
        """Get all campaigns using the official GetAll endpoint"""

        print("=== Fetching campaigns via /campaign/GetAll ===")

        url = f"{self.base_url}/campaign/GetAll"
        all_campaigns = []
        offset = 0
        limit = 100

        try:
            while True:
                print(f"Fetching campaigns (offset={offset}, limit={limit})...")

                body = {
                    "offset": offset,
                    "limit": limit
                }

                response = requests.post(url, headers=self.headers, json=body)
                print(f"Status: {response.status_code}")

                if response.status_code != 200:
                    print(f"Error: {response.text}")
                    return None

                result = response.json()
                campaigns = result.get("items", [])
                total_count = result.get("totalCount", 0)

                print(f"✓ Fetched {len(campaigns)} campaigns")
                print(f"✓ Total: {total_count}")

                if not campaigns:
                    break

                all_campaigns.extend(campaigns)

                # Check if we got all campaigns
                if len(all_campaigns) >= total_count or len(campaigns) < limit:
                    break

                offset += limit

            print(f"✓ Total campaigns fetched: {len(all_campaigns)}")

            return {
                "campaigns": all_campaigns,
                "totalCount": len(all_campaigns)
            }

        except Exception as e:
            print(f"Error fetching campaigns: {e}")
            import traceback
            traceback.print_exc()
            return None


# ===== ROUTES =====

@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session.get('username', 'User'))


@app.route('/api/download', methods=['POST'])
@login_required
def api_download():
    """Download conversations as CSV"""
    try:
        data = request.json
        # IMPORTANT: Use form API key FIRST, environment variable as fallback
        api_key = data.get('api_key', '').strip() or os.environ.get('HEYREACH_API_KEY')

        if not api_key:
            return jsonify({'error': 'Clé API requise. Veuillez entrer votre clé API HeyReach.'}), 400

        # Log which API key is being used
        if data.get('api_key', '').strip():
            print(f"[DOWNLOAD] Using API key from form: {api_key[:20]}...")
        else:
            print(f"[DOWNLOAD] Using API key from environment: {api_key[:20]}...")

        # Parse campaign IDs
        campaign_ids = data.get('campaign_ids', '')
        if isinstance(campaign_ids, str):
            campaign_ids = [int(x.strip()) for x in campaign_ids.split(',') if x.strip().isdigit()]
        elif isinstance(campaign_ids, list):
            campaign_ids = [int(x) for x in campaign_ids if str(x).strip().isdigit()]

        # Only pass campaign_ids if it's not empty
        filter_campaign_ids = campaign_ids if campaign_ids and len(campaign_ids) > 0 else None

        # Get date range if specified
        date_from = data.get('date_from')
        date_to = data.get('date_to')

        if date_from or date_to:
            print(f"[DOWNLOAD] Date range filter: {date_from} to {date_to}")

        # Initialize API
        api = HeyReachAPI(api_key)

        # Get conversations with date filtering
        conversations = api.get_all_conversations(
            campaign_ids=filter_campaign_ids,
            date_from=date_from,
            date_to=date_to
        )

        if not conversations:
            return jsonify({'error': 'No conversations found'}), 404

        # Create CSV in memory
        output = io.StringIO()

        if conversations:
            # Get all keys from all conversations
            all_keys = set()
            for conv in conversations:
                all_keys.update(conv.keys())

            # Write CSV
            writer = csv.DictWriter(output, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(conversations)

        output.seek(0)

        # Create response
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'heyreach_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/campaigns', methods=['POST'])
@login_required
def api_get_campaigns():
    """Get all campaigns from all workspaces"""
    try:
        data = request.json
        # IMPORTANT: Use form API key FIRST, environment variable as fallback
        api_key = data.get('api_key', '').strip() or os.environ.get('HEYREACH_API_KEY')

        if not api_key:
            return jsonify({'error': 'Clé API requise. Veuillez entrer votre clé API HeyReach.'}), 400

        # Log which API key is being used
        if data.get('api_key', '').strip():
            print(f"[CAMPAIGNS] Using API key from form: {api_key[:20]}...")
        else:
            print(f"[CAMPAIGNS] Using API key from environment: {api_key[:20]}...")


        # Initialize API
        api = HeyReachAPI(api_key)

        # Get campaigns
        print("Fetching campaigns...")
        result = api.get_campaigns()

        if not result:
            return jsonify({'error': 'Impossible de récupérer les campagnes. L\'API HeyReach ne retourne pas cette information.'}), 404

        # Handle different response formats
        campaigns = []
        if 'campaigns' in result:
            campaigns = result['campaigns']
        elif 'data' in result:
            campaigns = result['data']
        elif 'items' in result:
            campaigns = result['items']
        elif isinstance(result, list):
            campaigns = result

        if not campaigns:
            return jsonify({'error': 'Aucune campagne trouvée'}), 404

        # Sort by name
        campaigns.sort(key=lambda x: str(x.get('name', '')).lower())

        print(f"Returning {len(campaigns)} campaigns")

        return jsonify({
            'success': True,
            'campaigns': campaigns
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erreur: {str(e)}'}), 500


@app.route('/api/stats', methods=['POST'])
@login_required
def api_get_stats():
    """Get overall stats from HeyReach"""
    try:
        data = request.json
        # IMPORTANT: Use form API key FIRST, environment variable as fallback
        api_key = data.get('api_key', '').strip() or os.environ.get('HEYREACH_API_KEY')

        if not api_key:
            return jsonify({'error': 'Clé API requise. Veuillez entrer votre clé API HeyReach.'}), 400

        # Log which API key is being used
        if data.get('api_key', '').strip():
            print(f"[STATS] Using API key from form: {api_key[:20]}...")
        else:
            print(f"[STATS] Using API key from environment: {api_key[:20]}...")

        # Get parameters
        campaign_ids = data.get('campaign_ids', [])
        account_ids = data.get('account_ids', [])
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        print(f"[STATS] Getting stats from {start_date} to {end_date}")
        print(f"[STATS] Campaign IDs: {campaign_ids}")
        print(f"[STATS] Account IDs: {account_ids}")

        # Call HeyReach API
        url = "https://api.heyreach.io/api/public/stats/GetOverallStats"
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }

        body = {
            "accountIds": account_ids if account_ids else [],
            "campaignIds": campaign_ids if campaign_ids else [],
            "startDate": start_date,
            "endDate": end_date
        }

        response = requests.post(url, headers=headers, json=body)
        print(f"[STATS] Status: {response.status_code}")

        if response.status_code != 200:
            print(f"[STATS] Error: {response.text}")
            return jsonify({'error': 'Erreur lors de la récupération des stats'}), response.status_code

        result = response.json()
        print(f"[STATS] Success")

        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erreur: {str(e)}'}), 500


@app.route('/health')
def health():
    """Health check endpoint for Render"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', 'False') == 'True')
