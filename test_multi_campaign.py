#!/usr/bin/env python3
"""
Script de test pour vérifier le fonctionnement multi-campagne du link tracker
Test des campagnes: aura.camp et wesser-recrutement.fr
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = input("URL de votre app Render (ex: https://votre-app.onrender.com): ").strip()
if not BASE_URL:
    BASE_URL = "http://localhost:5000"

print(f"\n🔧 Test du link tracker sur: {BASE_URL}")
print("=" * 60)

# Test 1: Créer des liens pour aura.camp
print("\n📋 Test 1: Création de liens pour AURA.CAMP")
print("-" * 60)

aura_links = []
aura_prospects = [
    {"first_name": "Sophie", "last_name": "Martin", "email": "sophie@test-aura.com"},
    {"first_name": "Thomas", "last_name": "Bernard", "email": "thomas@test-aura.com"},
    {"first_name": "Emma", "last_name": "Dubois", "email": "emma@test-aura.com"}
]

for prospect in aura_prospects:
    payload = {
        "first_name": prospect["first_name"],
        "last_name": prospect["last_name"],
        "email": prospect["email"],
        "campaign": "aura.camp",
        "destination_url": "https://aura.camp/demo"
    }

    try:
        response = requests.post(f"{BASE_URL}/api/create-link", json=payload, timeout=10)
        if response.status_code == 201:
            data = response.json()
            aura_links.append(data)
            print(f"✅ {prospect['first_name']} {prospect['last_name']}: {data['short_url']}")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Erreur réseau: {e}")

# Test 2: Créer des liens pour wesser-recrutement.fr
print("\n📋 Test 2: Création de liens pour WESSER-RECRUTEMENT.FR")
print("-" * 60)

wesser_links = []
wesser_prospects = [
    {"first_name": "Pierre", "last_name": "Dupont", "email": "pierre@test-wesser.fr"},
    {"first_name": "Marie", "last_name": "Leroy", "email": "marie@test-wesser.fr"},
    {"first_name": "Lucas", "last_name": "Moreau", "email": "lucas@test-wesser.fr"}
]

for prospect in wesser_prospects:
    payload = {
        "first_name": prospect["first_name"],
        "last_name": prospect["last_name"],
        "email": prospect["email"],
        "campaign": "wesser-recrutement.fr",
        "destination_url": "https://wesser-recrutement.fr/rejoindre"
    }

    try:
        response = requests.post(f"{BASE_URL}/api/create-link", json=payload, timeout=10)
        if response.status_code == 201:
            data = response.json()
            wesser_links.append(data)
            print(f"✅ {prospect['first_name']} {prospect['last_name']}: {data['short_url']}")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Erreur réseau: {e}")

# Test 3: Simuler des clics
print("\n📋 Test 3: Simulation de clics")
print("-" * 60)

print("\n🔹 Clics sur liens AURA (2 clics sur chaque lien)")
for link in aura_links[:2]:  # Simuler clics sur 2 premiers liens Aura
    try:
        # Premier clic
        response = requests.get(link['short_url'], allow_redirects=False, timeout=5)
        print(f"✅ Clic 1 sur {link['short_url']}")
        time.sleep(0.5)

        # Deuxième clic (même personne)
        response = requests.get(link['short_url'], allow_redirects=False, timeout=5)
        print(f"✅ Clic 2 sur {link['short_url']}")
    except Exception as e:
        print(f"⚠️  Erreur clic: {e}")

print("\n🔹 Clics sur liens WESSER (1 clic sur chaque lien)")
for link in wesser_links:  # Simuler 1 clic sur tous les liens Wesser
    try:
        response = requests.get(link['short_url'], allow_redirects=False, timeout=5)
        print(f"✅ Clic sur {link['short_url']}")
        time.sleep(0.5)
    except Exception as e:
        print(f"⚠️  Erreur clic: {e}")

# Attendre que les données soient enregistrées
print("\n⏳ Attente de 2 secondes pour enregistrement des clics...")
time.sleep(2)

# Test 4: Vérifier les analytics globales
print("\n📋 Test 4: Analytics GLOBALES (toutes campagnes)")
print("-" * 60)

try:
    response = requests.get(f"{BASE_URL}/api/analytics", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Total Liens: {data['total_links']}")
        print(f"✅ Total Clics: {data['total_clicks']}")
        print(f"✅ Unique Visitors: {data['unique_clicks']}")
        print(f"✅ Click Rate: {data['click_rate']}%")

        print("\n📊 Campagnes détectées:")
        for campaign in data.get('campaigns', []):
            print(f"   - {campaign['campaign']}: {campaign['clicks']} clics")
    else:
        print(f"❌ Erreur: {response.status_code}")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 5: Analytics filtrées par AURA
print("\n📋 Test 5: Analytics AURA.CAMP uniquement")
print("-" * 60)

try:
    response = requests.get(f"{BASE_URL}/api/analytics?campaign=aura.camp", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Total Liens (Aura): {data['total_links']}")
        print(f"✅ Total Clics (Aura): {data['total_clicks']}")
        print(f"✅ Unique Visitors (Aura): {data['unique_clicks']}")
        print(f"✅ Click Rate (Aura): {data['click_rate']}%")
    else:
        print(f"❌ Erreur: {response.status_code}")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 6: Analytics filtrées par WESSER
print("\n📋 Test 6: Analytics WESSER-RECRUTEMENT.FR uniquement")
print("-" * 60)

try:
    response = requests.get(f"{BASE_URL}/api/analytics?campaign=wesser-recrutement.fr", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Total Liens (Wesser): {data['total_links']}")
        print(f"✅ Total Clics (Wesser): {data['total_clicks']}")
        print(f"✅ Unique Visitors (Wesser): {data['unique_clicks']}")
        print(f"✅ Click Rate (Wesser): {data['click_rate']}%")
    else:
        print(f"❌ Erreur: {response.status_code}")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 7: Liste des campagnes disponibles
print("\n📋 Test 7: Liste des campagnes disponibles")
print("-" * 60)

try:
    response = requests.get(f"{BASE_URL}/api/campaigns", timeout=10)
    if response.status_code == 200:
        campaigns = response.json()
        print(f"✅ Campagnes disponibles ({len(campaigns)}):")
        for campaign in campaigns:
            print(f"   - {campaign}")
    else:
        print(f"❌ Erreur: {response.status_code}")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 8: Détails des clics
print("\n📋 Test 8: Détails des clics par campagne")
print("-" * 60)

print("\n🔹 Clics AURA:")
try:
    response = requests.get(f"{BASE_URL}/api/clicks?campaign=aura.camp", timeout=10)
    if response.status_code == 200:
        clicks = response.json()
        for click in clicks[:3]:  # Afficher les 3 premiers
            print(f"   {click['first_name']} {click['last_name']}: {click['click_count']} clics")
    else:
        print(f"❌ Erreur: {response.status_code}")
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n🔹 Clics WESSER:")
try:
    response = requests.get(f"{BASE_URL}/api/clicks?campaign=wesser-recrutement.fr", timeout=10)
    if response.status_code == 200:
        clicks = response.json()
        for click in clicks[:3]:  # Afficher les 3 premiers
            print(f"   {click['first_name']} {click['last_name']}: {click['click_count']} clics")
    else:
        print(f"❌ Erreur: {response.status_code}")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Résumé final
print("\n" + "=" * 60)
print("✅ Tests terminés !")
print("=" * 60)
print(f"\n📊 Résumé:")
print(f"   - {len(aura_links)} liens créés pour aura.camp")
print(f"   - {len(wesser_links)} liens créés pour wesser-recrutement.fr")
print(f"   - Clics simulés sur les liens")
print(f"\n🌐 Vérifiez le dashboard: {BASE_URL}/")
print(f"   → Filtrez par campagne pour voir la séparation des stats")
print("\n💡 Prochaines étapes:")
print("   1. Ouvrir le dashboard")
print("   2. Tester le filtre de campagne (All / aura.camp / wesser-recrutement.fr)")
print("   3. Vérifier que les stats sont bien séparées")
print("   4. Exporter le CSV pour chaque campagne")
print("")
