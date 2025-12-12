"""
HeyReach Exporter - Simple Integration
Route unique /heyreach qui affiche le dashboard directement
"""

from flask import render_template, request, jsonify, send_file
import requests
import io
import csv
from datetime import datetime
import os
import json

# Optional imports for reporting features
try:
    from PIL import Image, ImageDraw, ImageFont
    from anthropic import Anthropic
    REPORTING_AVAILABLE = True
except ImportError:
    REPORTING_AVAILABLE = False
    print("Warning: PIL or anthropic not available. Reporting features disabled.")

def init_heyreach_routes(app):
    """Initialize HeyReach routes in the main app"""

    # HeyReach API Client
    class HeyReachAPI:
        def __init__(self, api_key):
            self.api_key = api_key
            self.base_url = "https://api.heyreach.io/api/public"
            self.headers = {
                "X-API-KEY": api_key,
                "Content-Type": "application/json"
            }

        def get_conversations(self, campaign_ids=None, linkedin_account_ids=None, date_from=None, date_to=None, offset=0, limit=100):
            url = f"{self.base_url}/inbox/GetConversationsV2"
            body = {
                "offset": offset,
                "limit": limit
            }
            if campaign_ids:
                body["campaignIds"] = campaign_ids
            if linkedin_account_ids:
                body["linkedInAccountIds"] = linkedin_account_ids

            response = requests.post(url, headers=self.headers, json=body)
            if response.status_code != 200:
                raise Exception(f"API Error: {response.text}")

            return response.json()

        def get_all_conversations(self, campaign_ids=None, linkedin_account_ids=None, date_from=None, date_to=None):
            all_conversations = []
            offset = 0
            limit = 100
            max_iterations = 1000

            for iteration in range(max_iterations):
                result = self.get_conversations(campaign_ids, linkedin_account_ids, date_from, date_to, offset, limit)
                conversations = result.get("items", [])
                total_count = result.get("totalCount", 0)

                if not conversations:
                    break

                all_conversations.extend(conversations)

                if len(all_conversations) >= total_count or len(conversations) < limit:
                    break

                offset += limit

            # Filter by date if specified
            if date_from or date_to:
                filtered_conversations = []
                for conv in all_conversations:
                    last_msg_date = conv.get('lastMessageAt')
                    if not last_msg_date:
                        continue

                    msg_date = datetime.fromisoformat(last_msg_date.replace('Z', '+00:00')).date()

                    if date_from:
                        from_date = datetime.fromisoformat(date_from).date()
                        if msg_date < from_date:
                            continue

                    if date_to:
                        to_date = datetime.fromisoformat(date_to).date()
                        if msg_date > to_date:
                            continue

                    filtered_conversations.append(conv)

                return filtered_conversations

            return all_conversations

        def get_campaigns(self):
            url = f"{self.base_url}/campaign/GetAll"
            all_campaigns = []
            offset = 0
            limit = 100

            while True:
                body = {"offset": offset, "limit": limit}
                response = requests.post(url, headers=self.headers, json=body)

                if response.status_code != 200:
                    return None

                result = response.json()
                campaigns = result.get("items", [])
                total_count = result.get("totalCount", 0)

                if not campaigns:
                    break

                all_campaigns.extend(campaigns)

                if len(all_campaigns) >= total_count or len(campaigns) < limit:
                    break

                offset += limit

            return {"campaigns": all_campaigns, "totalCount": len(all_campaigns)}

    # ===== ROUTES =====

    @app.route('/heyreach')
    def heyreach():
        """HeyReach Exporter - Main page"""
        return render_template('heyreach.html')

    @app.route('/heyreach/api/campaigns', methods=['POST'])
    def heyreach_api_campaigns():
        """Get all campaigns"""
        try:
            data = request.json
            api_key = data.get('api_key', '').strip() or os.environ.get('HEYREACH_API_KEY')

            if not api_key:
                return jsonify({'error': 'Clé API requise'}), 400

            api = HeyReachAPI(api_key)
            result = api.get_campaigns()

            if not result:
                return jsonify({'error': 'Impossible de récupérer les campagnes'}), 404

            campaigns = result.get('campaigns', [])
            campaigns.sort(key=lambda x: str(x.get('name', '')).lower())

            return jsonify({'success': True, 'campaigns': campaigns})

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/heyreach/api/stats', methods=['POST'])
    def heyreach_api_stats():
        """Get overall stats"""
        try:
            data = request.json
            api_key = data.get('api_key', '').strip() or os.environ.get('HEYREACH_API_KEY')

            if not api_key:
                return jsonify({'error': 'Clé API requise'}), 400

            campaign_ids = data.get('campaign_ids', [])
            account_ids = data.get('account_ids', [])
            start_date = data.get('start_date')
            end_date = data.get('end_date')

            url = "https://api.heyreach.io/api/public/stats/GetOverallStats"
            headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
            body = {
                "accountIds": account_ids if account_ids else [],
                "campaignIds": campaign_ids if campaign_ids else [],
                "startDate": start_date,
                "endDate": end_date
            }

            response = requests.post(url, headers=headers, json=body)

            if response.status_code != 200:
                return jsonify({'error': 'Erreur lors de la récupération des stats'}), response.status_code

            return jsonify(response.json())

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/heyreach/api/download', methods=['POST'])
    def heyreach_api_download():
        """Download conversations as CSV"""
        try:
            data = request.json
            api_key = data.get('api_key', '').strip() or os.environ.get('HEYREACH_API_KEY')

            if not api_key:
                return jsonify({'error': 'Clé API requise'}), 400

            campaign_ids = data.get('campaign_ids', [])
            if isinstance(campaign_ids, str):
                campaign_ids = [int(x.strip()) for x in campaign_ids.split(',') if x.strip().isdigit()]
            elif isinstance(campaign_ids, list):
                campaign_ids = [int(x) for x in campaign_ids if str(x).strip().isdigit()]

            filter_campaign_ids = campaign_ids if campaign_ids and len(campaign_ids) > 0 else None

            date_from = data.get('date_from')
            date_to = data.get('date_to')

            api = HeyReachAPI(api_key)
            conversations = api.get_all_conversations(
                campaign_ids=filter_campaign_ids,
                date_from=date_from,
                date_to=date_to
            )

            # Create CSV
            output = io.StringIO()
            writer = csv.writer(output)

            writer.writerow([
                'Campaign ID', 'Campaign Name', 'Lead Name', 'Profile URL',
                'Last Message', 'Last Message Date', 'Total Messages',
                'Conversation ID', 'LinkedIn Sender'
            ])

            for conv in conversations:
                profile = conv.get('correspondentProfile', {})
                lead_name = f"{profile.get('firstName', '')} {profile.get('lastName', '')}".strip()

                writer.writerow([
                    conv.get('campaignId', ''),
                    conv.get('campaignName', ''),
                    lead_name or 'N/A',
                    profile.get('profileUrl', ''),
                    conv.get('lastMessageText', ''),
                    conv.get('lastMessageAt', ''),
                    conv.get('totalMessages', 0),
                    conv.get('conversationId', ''),
                    conv.get('linkedInSenderName', '')
                ])

            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'heyreach_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            )

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/heyreach/api/analyze-hot-leads', methods=['POST'])
    def heyreach_api_analyze_hot_leads():
        """Analyze conversations and return hot leads with AI categorization"""
        try:
            # Vérifier si le reporting est disponible
            if not REPORTING_AVAILABLE:
                return jsonify({
                    'error': 'Fonctionnalité de reporting non disponible. Installez les dépendances: pip install Pillow anthropic',
                    'hot_leads': [],
                    'total_analyzed': 0,
                    'hot_count': 0
                }), 200

            # Import avec gestion d'erreur
            try:
                from heyreach_reporting import analyze_conversations
            except ImportError as e:
                return jsonify({
                    'error': f'Module heyreach_reporting non disponible: {str(e)}',
                    'hot_leads': [],
                    'total_analyzed': 0,
                    'hot_count': 0
                }), 200

            data = request.json
            api_key = data.get('api_key', '').strip() or os.environ.get('HEYREACH_API_KEY')

            if not api_key:
                return jsonify({'error': 'Clé API requise'}), 400

            campaign_ids = data.get('campaign_ids', [])
            if isinstance(campaign_ids, str):
                campaign_ids = [int(x.strip()) for x in campaign_ids.split(',') if x.strip().isdigit()]
            elif isinstance(campaign_ids, list):
                campaign_ids = [int(x) for x in campaign_ids if str(x).strip().isdigit()]

            filter_campaign_ids = campaign_ids if campaign_ids and len(campaign_ids) > 0 else None

            date_from = data.get('date_from')
            date_to = data.get('date_to')

            api = HeyReachAPI(api_key)
            conversations = api.get_all_conversations(
                campaign_ids=filter_campaign_ids,
                date_from=date_from,
                date_to=date_to
            )

            # Analyser avec l'IA
            analysis = analyze_conversations(conversations)

            return jsonify(analysis)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/heyreach/api/generate-report', methods=['POST'])
    def heyreach_api_generate_report():
        """Generate PNG report with stats and hot leads"""
        try:
            # Vérifier si le reporting est disponible
            if not REPORTING_AVAILABLE:
                return jsonify({
                    'error': 'Fonctionnalité de reporting non disponible. Installez les dépendances: pip install Pillow anthropic'
                }), 400

            try:
                from heyreach_reporting import generate_report_image
            except ImportError as e:
                return jsonify({
                    'error': f'Module heyreach_reporting non disponible: {str(e)}'
                }), 400

            data = request.json
            api_key = data.get('api_key', '').strip() or os.environ.get('HEYREACH_API_KEY')

            if not api_key:
                return jsonify({'error': 'Clé API requise'}), 400

            # Get stats
            campaign_ids = data.get('campaign_ids', [])
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            time_period = data.get('time_period', 'All time')

            # Get stats from HeyReach
            url = "https://api.heyreach.io/api/public/stats/GetOverallStats"
            headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
            body = {
                "accountIds": [],
                "campaignIds": campaign_ids if campaign_ids else [],
                "startDate": start_date,
                "endDate": end_date
            }

            stats_response = requests.post(url, headers=headers, json=body)
            if stats_response.status_code != 200:
                return jsonify({'error': 'Erreur lors de la récupération des stats'}), 500

            stats = stats_response.json()

            # Get hot leads from request
            hot_leads = data.get('hot_leads', [])

            # Generate image
            img_buffer = generate_report_image(stats, hot_leads, time_period)

            return send_file(
                img_buffer,
                mimetype='image/png',
                as_attachment=True,
                download_name=f'heyreach_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            )

        except Exception as e:
            return jsonify({'error': str(e)}), 500
