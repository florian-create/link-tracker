"""
HeyReach Reporting Module
Génération de rapports PNG avec catégorisation IA des leads chauds
"""

import io
import json
import os
from datetime import datetime

# Optional imports for AI and image generation
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    Anthropic = None

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = ImageDraw = ImageFont = None

# Configuration Claude API
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
anthropic_client = None
if ANTHROPIC_API_KEY and ANTHROPIC_AVAILABLE:
    anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

def categorize_lead(conversation, last_message_text):
    """
    Catégorise un lead comme CHAUD, TIEDE ou FROID avec Claude 3.5 Haiku

    Args:
        conversation: Dict avec les infos de la conversation
        last_message_text: Le dernier message reçu

    Returns:
        Dict avec:
        - category: "hot", "warm", "cold"
        - confidence: 0-100
        - key_phrase: L'extrait le plus marquant du message
        - reason: Raison de la catégorisation
    """
    if not ANTHROPIC_AVAILABLE:
        return {
            "category": "unknown",
            "confidence": 0,
            "key_phrase": last_message_text[:100] if last_message_text else "",
            "reason": "anthropic library not installed"
        }

    if not anthropic_client or not last_message_text:
        return {
            "category": "unknown",
            "confidence": 0,
            "key_phrase": last_message_text[:100] if last_message_text else "",
            "reason": "API key missing or no message"
        }

    try:
        # Utiliser Claude 3.5 Haiku - très rapide et pas cher (~$0.25/MTok)
        response = anthropic_client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=300,
            temperature=0,
            messages=[{
                "role": "user",
                "content": f"""Analyse ce message LinkedIn et catégorise le lead:

MESSAGE: "{last_message_text}"

Catégorise ce lead en:
- HOT (chaud): Montre un intérêt fort, demande des infos, veut un RDV, parle de budget/timing
- WARM (tiède): Intérêt modéré, pose des questions mais pas engagé
- COLD (froid): Refus poli, pas intéressé, ou réponse vague

Réponds UNIQUEMENT en JSON valide:
{{
    "category": "hot|warm|cold",
    "confidence": 0-100,
    "key_phrase": "l'extrait le plus marquant du message (max 100 chars)",
    "reason": "raison courte de la catégorisation"
}}"""
            }]
        )

        # Extraire le texte de la réponse
        response_text = response.content[0].text.strip()

        # Parser le JSON
        result = json.loads(response_text)

        return result

    except Exception as e:
        print(f"Error categorizing lead: {e}")
        return {
            "category": "unknown",
            "confidence": 0,
            "key_phrase": last_message_text[:100] if last_message_text else "",
            "reason": f"Error: {str(e)}"
        }


def analyze_conversations(conversations):
    """
    Analyse toutes les conversations et retourne uniquement les leads chauds

    Args:
        conversations: Liste de conversations de l'API HeyReach

    Returns:
        Dict avec:
        - hot_leads: Liste des leads chauds avec extraits
        - total_analyzed: Nombre total de conversations analysées
        - hot_count: Nombre de leads chauds trouvés
    """
    hot_leads = []

    for conv in conversations:
        last_message = conv.get('lastMessageText', '')

        # Skip si pas de message ou si c'est nous qui avons envoyé le dernier message
        if not last_message:
            continue

        # Catégoriser avec l'IA
        analysis = categorize_lead(conv, last_message)

        # Garder seulement les leads chauds (hot)
        if analysis['category'] == 'hot':
            profile = conv.get('correspondentProfile', {})
            hot_leads.append({
                'name': f"{profile.get('firstName', '')} {profile.get('lastName', '')}".strip(),
                'company': profile.get('company', ''),
                'title': profile.get('headline', ''),
                'message_extract': analysis['key_phrase'],
                'confidence': analysis['confidence'],
                'campaign': conv.get('campaignName', ''),
                'date': conv.get('lastMessageAt', ''),
                'profile_url': profile.get('profileUrl', '')
            })

    return {
        'hot_leads': hot_leads,
        'total_analyzed': len(conversations),
        'hot_count': len(hot_leads)
    }


def generate_report_image(stats, hot_leads, time_period="All time"):
    """
    Génère une image PNG du rapport avec stats et leads chauds

    Args:
        stats: Dict avec les statistiques (overallStats de l'API)
        hot_leads: Liste des leads chauds (de analyze_conversations)
        time_period: Période du rapport (ex: "Last 7 days", "All time")

    Returns:
        BytesIO contenant l'image PNG
    """
    if not PIL_AVAILABLE:
        raise ImportError("Pillow is required for image generation. Install with: pip install Pillow")

    # Dimensions de l'image
    width = 1200
    header_height = 200
    stats_height = 180
    lead_height = 100
    padding = 40

    # Calculer hauteur totale
    total_height = header_height + stats_height + (len(hot_leads) * lead_height) + (padding * 3)

    # Créer l'image
    img = Image.new('RGB', (width, total_height), color='#0a0a0a')
    draw = ImageDraw.Draw(img)

    # Charger les fonts (utiliser font par défaut si pas de font custom)
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        font_subtitle = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        font_stat_label = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
        font_stat_value = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        font_lead_name = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        font_lead_text = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = font_title
        font_stat_label = font_title
        font_stat_value = font_title
        font_lead_name = font_title
        font_lead_text = font_title

    y = padding

    # === HEADER ===
    draw.text((padding, y), "HEYREACH REPORT", fill='#ffffff', font=font_title)
    y += 60
    draw.text((padding, y), f"Period: {time_period}", fill='#888888', font=font_subtitle)
    y += 40
    draw.text((padding, y), f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", fill='#666666', font=font_subtitle)
    y += 60

    # Ligne de séparation
    draw.rectangle([(padding, y), (width - padding, y + 2)], fill='#222222')
    y += padding

    # === STATS ===
    overall = stats.get('overallStats', {})

    stat_items = [
        ("Messages Sent", overall.get('messagesSent', 0)),
        ("Replies", overall.get('totalMessageReplies', 0)),
        ("Reply Rate", f"{(overall.get('messageReplyRate', 0) * 100):.1f}%"),
        ("Hot Leads", len(hot_leads))
    ]

    stat_width = (width - (padding * 2)) // 4
    x = padding

    for label, value in stat_items:
        # Label
        draw.text((x, y), label, fill='#888888', font=font_stat_label)
        # Value
        draw.text((x, y + 30), str(value), fill='#4ade80' if 'Hot' in label else '#ffffff', font=font_stat_value)
        x += stat_width

    y += 120

    # Ligne de séparation
    draw.rectangle([(padding, y), (width - padding, y + 2)], fill='#222222')
    y += padding

    # === HOT LEADS ===
    draw.text((padding, y), f"🔥 {len(hot_leads)} Hot Leads", fill='#ffffff', font=font_subtitle)
    y += 50

    for i, lead in enumerate(hot_leads[:20]):  # Limiter à 20 leads
        # Background pour chaque lead
        lead_bg_y = y
        draw.rectangle(
            [(padding, lead_bg_y), (width - padding, lead_bg_y + lead_height - 10)],
            fill='#111111',
            outline='#222222'
        )

        # Nom et entreprise
        name_company = f"{lead['name']}"
        if lead.get('company'):
            name_company += f" • {lead['company']}"
        draw.text((padding + 20, y + 15), name_company, fill='#ffffff', font=font_lead_name)

        # Extrait du message
        message_text = f'"{lead["message_extract"]}"'
        # Limiter la longueur
        if len(message_text) > 120:
            message_text = message_text[:117] + '..."'
        draw.text((padding + 20, y + 45), message_text, fill='#4ade80', font=font_lead_text)

        y += lead_height

    # Convertir en BytesIO
    output = io.BytesIO()
    img.save(output, format='PNG')
    output.seek(0)

    return output


def generate_csv_with_full_conversations(conversations):
    """
    Génère un CSV avec toutes les conversations complètes

    TODO: Implémenter la récupération des messages complets depuis l'API
    Pour l'instant, retourne les conversations avec le dernier message
    """
    output = io.StringIO()
    import csv
    writer = csv.writer(output)

    writer.writerow([
        'Campaign ID', 'Campaign Name', 'Lead Name', 'Company', 'Title',
        'Profile URL', 'Total Messages', 'Last Message', 'Last Message Date',
        'Conversation ID', 'LinkedIn Sender', 'Full Conversation'
    ])

    for conv in conversations:
        profile = conv.get('correspondentProfile', {})
        lead_name = f"{profile.get('firstName', '')} {profile.get('lastName', '')}".strip()

        # TODO: Récupérer tous les messages de la conversation
        # Pour l'instant, on met juste le dernier message
        full_conversation = conv.get('lastMessageText', '')

        writer.writerow([
            conv.get('campaignId', ''),
            conv.get('campaignName', ''),
            lead_name or 'N/A',
            profile.get('company', ''),
            profile.get('headline', ''),
            profile.get('profileUrl', ''),
            conv.get('totalMessages', 0),
            conv.get('lastMessageText', ''),
            conv.get('lastMessageAt', ''),
            conv.get('conversationId', ''),
            conv.get('linkedInSenderName', ''),
            full_conversation
        ])

    output.seek(0)
    return output
