// Global app configuration and utilities

console.log('HeyReach Exporter loaded!');

// Utility function to format numbers
function formatNumber(num) {
    return new Intl.NumberFormat('fr-FR').format(num);
}

// Utility function to format dates
function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    const style = document.createElement('style');
    style.textContent = `
        .toast {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 9999;
            animation: slideIn 0.3s ease;
        }
        .toast-success { border-left: 4px solid #51cf66; }
        .toast-error { border-left: 4px solid #ff6b6b; }
        .toast-info { border-left: 4px solid #667eea; }
        @keyframes slideIn {
            from { transform: translateX(400px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Handle API errors
function handleApiError(error) {
    console.error('API Error:', error);
    showToast(error.message || 'Une erreur est survenue', 'error');
}

// Validate form inputs
function validateForm(formData) {
    if (!formData.api_key && !window.API_KEY_CONFIGURED) {
        throw new Error('Clé API requise');
    }
    return true;
}

// Save API key to localStorage for convenience
function saveApiKey(apiKey) {
    if (apiKey && apiKey.trim()) {
        localStorage.setItem('heyreach_api_key', apiKey);
    }
}

function loadApiKey() {
    const savedKey = localStorage.getItem('heyreach_api_key');
    if (savedKey) {
        const apiKeyInput = document.getElementById('api_key');
        if (apiKeyInput) {
            apiKeyInput.value = savedKey;
        }
    }
}

// Load API key on page load
if (document.getElementById('api_key')) {
    loadApiKey();
}

// Export current stats as JSON
function exportStatsAsJSON() {
    const stats = {
        total: document.getElementById('stat-total')?.textContent,
        reply_rate: document.getElementById('stat-reply-rate')?.textContent,
        hot_leads: document.getElementById('stat-hot-leads')?.textContent,
        avg_messages: document.getElementById('stat-avg-messages')?.textContent,
        timestamp: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(stats, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `heyreach_stats_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

// Print current page
function printPage() {
    window.print();
}
