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
import time

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

        def get_conversation_with_messages(self, account_id, conversation_id):
            """Get a conversation with all its messages using GetChatroom endpoint"""
            url = f"{self.base_url}/inbox/GetChatroom/{account_id}/{conversation_id}"

            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code != 200:
                    print(f"API Error for conversation {conversation_id}: {response.status_code} - {response.text}")
                    return []

                result = response.json()

                # L'endpoint GetChatroom retourne la conversation avec ses messages
                messages = result.get("messages", [])

                if not messages:
                    print(f"No messages found for conversation {conversation_id}")
                    return []

                # Trier les messages par date (ordre chronologique)
                messages.sort(key=lambda x: x.get('createdAt', ''))

                return messages
            except Exception as e:
                print(f"Error fetching messages for conversation {conversation_id}: {e}")
                return []

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
        """Download conversations as CSV with full message history (30 columns)"""
        try:
            data = request.json
            api_key = data.get('api_key', '').strip() or os.environ.get('HEYREACH_API_KEY')
            workspace_name = data.get('workspace_name', 'export')

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

            # NEW: Quick mode - skip fetching individual messages
            quick_mode = data.get('quick_mode', False)

            api = HeyReachAPI(api_key)

            # Get all campaigns to create a mapping campaignId -> campaignName
            campaigns_data = api.get_campaigns()
            campaign_mapping = {}
            if campaigns_data and campaigns_data.get('campaigns'):
                for camp in campaigns_data['campaigns']:
                    campaign_mapping[camp.get('id')] = camp.get('name', f"Campaign {camp.get('id')}")

            conversations = api.get_all_conversations(
                campaign_ids=filter_campaign_ids,
                date_from=date_from,
                date_to=date_to
            )

            total_conversations = len(conversations)
            print(f"Total conversations to export: {total_conversations}")

            # Log estimate for large exports
            if total_conversations > 100:
                estimated_time = total_conversations * 0.2
                print(f"Estimated export time: ~{estimated_time:.0f} seconds ({estimated_time/60:.1f} minutes)")
                if total_conversations > 1000:
                    print(f"LARGE EXPORT: {total_conversations} conversations - this will take a while!")

            # Get stats for the header row
            start_date = None
            end_date = None
            if date_from and date_to:
                # Convert YYYY-MM-DD to ISO format
                start_date = f"{date_from}T00:00:00.000Z"
                end_date = f"{date_to}T23:59:59.999Z"

            stats_url = "https://api.heyreach.io/api/public/stats/GetOverallStats"
            headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
            stats_body = {
                "accountIds": [],
                "campaignIds": filter_campaign_ids if filter_campaign_ids else [],
                "startDate": start_date,
                "endDate": end_date
            }
            try:
                stats_response = requests.post(stats_url, headers=headers, json=stats_body)
                if stats_response.status_code == 200:
                    stats = stats_response.json().get('overallStats', {})
                else:
                    stats = {}
            except:
                stats = {}

            # Create CSV
            output = io.StringIO()
            writer = csv.writer(output)

            # First row: Stats summary
            connections_sent = stats.get('connectionsSent', 0)
            connections_accepted = stats.get('connectionsAccepted', 0)
            messages_sent = stats.get('messagesSent', 0)
            replies = stats.get('totalMessageReplies', 0)

            writer.writerow([
                f'STATS: Connexions: {connections_sent} envoyées | {connections_accepted} acceptées | Messages: {messages_sent} envoyés | {replies} réponses'
            ])
            writer.writerow([])  # Empty row

            # Header with all useful lead info
            header = [
                'Lead Name',
                'Company',
                'Position',
                'Location',
                'Profile URL',
                'Campaign',
                'LinkedIn Account',
                'Last Message Date',
                'Total Messages',
                'Last Message',
                'Tags'
            ]

            # In full mode, add 30 message columns
            if not quick_mode:
                header.insert(7, 'First Message Date')  # Add after LinkedIn Account
                for i in range(1, 31):
                    header.append(f'Message_{i}')

            writer.writerow(header)

            # Write data
            total_convs = len(conversations)
            for idx, conv in enumerate(conversations):
                if idx % 50 == 0:
                    print(f"Processing conversation {idx+1}/{total_convs}...")

                profile = conv.get('correspondentProfile', {})
                lead_name = f"{profile.get('firstName', '')} {profile.get('lastName', '')}".strip()
                conversation_id = conv.get('id', '')
                account_id = conv.get('linkedInAccountId', '')

                # Get LinkedIn account info
                linkedin_account = conv.get('linkedInAccount', {})
                linkedin_account_name = f"{linkedin_account.get('firstName', '')} {linkedin_account.get('lastName', '')}".strip()

                # Get campaign name from mapping
                campaign_id = conv.get('campaignId')
                campaign_name = campaign_mapping.get(campaign_id, f"Campaign {campaign_id}")

                # Get tags as comma-separated string
                tags = ', '.join(profile.get('tags', []))

                if quick_mode:
                    # QUICK MODE: Use only data from conversation object (no additional API calls)
                    last_message_date = conv.get('lastMessageAt', '')
                    last_message_text = conv.get('lastMessageText', '')

                    row = [
                        lead_name or 'N/A',
                        profile.get('companyName', ''),
                        profile.get('position', '') or profile.get('headline', ''),
                        profile.get('location', ''),
                        profile.get('profileUrl', ''),
                        campaign_name,
                        linkedin_account_name or linkedin_account.get('emailAddress', ''),
                        last_message_date,
                        conv.get('totalMessages', 0),
                        last_message_text or '',
                        tags
                    ]
                else:
                    # FULL MODE: Fetch all messages for each conversation
                    try:
                        messages = api.get_conversation_with_messages(account_id, conversation_id)
                        time.sleep(0.02)
                    except Exception as e:
                        print(f"Error fetching messages for conversation {conversation_id}: {e}")
                        messages = []

                    # Get first and last message dates
                    first_message_date = messages[0].get('createdAt', '') if messages else ''
                    last_message_date = messages[-1].get('createdAt', '') if messages else conv.get('lastMessageAt', '')

                    # Extract message text from 'body' field and format with sender
                    message_texts = []
                    for msg in messages[:30]:  # Limit to 30 messages
                        sender = msg.get('sender', 'UNKNOWN')
                        sender_label = 'ME' if sender == 'ME' else 'LEAD'
                        body = msg.get('body', '')
                        message_text = f"[{sender_label}] {body}" if body else ""
                        message_texts.append(message_text)

                    # Pad with empty strings if less than 30 messages
                    while len(message_texts) < 30:
                        message_texts.append('')

                    row = [
                        lead_name or 'N/A',
                        profile.get('companyName', ''),
                        profile.get('position', '') or profile.get('headline', ''),
                        profile.get('location', ''),
                        profile.get('profileUrl', ''),
                        campaign_name,
                        linkedin_account_name or linkedin_account.get('emailAddress', ''),
                        first_message_date,
                        last_message_date,
                        conv.get('totalMessages', 0),
                        tags
                    ]
                    # Add all 30 message columns
                    row.extend(message_texts)

                writer.writerow(row)

            output.seek(0)

            # Generate filename with workspace name and exact time
            now = datetime.now()
            filename = f"{workspace_name}_{now.strftime('%Y%m%d_%H%M%S')}.csv"

            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=filename
            )

        except Exception as e:
            return jsonify({'error': str(e)}), 500

