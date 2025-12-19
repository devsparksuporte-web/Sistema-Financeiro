// Funções utilitárias globais
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

function formatDateTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer') || document.querySelector('.toast-container');
    if (!container) return;
    
    const toastId = 'toast-' + Date.now();
    const icons = {
        info: 'info-circle',
        success: 'check-circle',
        warning: 'exclamation-triangle',
        error: 'times-circle'
    };
    const colors = {
        info: 'primary',
        success: 'success',
        warning: 'warning',
        error: 'danger'
    };
    
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = 'toast';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="toast-header bg-${colors[type] || 'primary'} text-white">
            <i class="fas fa-${icons[type] || 'info-circle'} me-2"></i>
            <strong class="me-auto">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    container.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast, { delay: 5000 });
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', function () {
        toast.remove();
    });
}

// Atalhos de teclado
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey) {
        switch(e.key) {
            case '1':
                if (window.location.pathname !== '/dashboard') {
                    e.preventDefault();
                    window.location.href = '/dashboard';
                }
                break;
            case '2':
                if (window.location.pathname !== '/precificacao') {
                    e.preventDefault();
                    window.location.href = '/precificacao';
                }
                break;
            case '3':
                if (window.location.pathname !== '/gerencial') {
                    e.preventDefault();
                    window.location.href = '/gerencial';
                }
                break;
            case '4':
                if (window.location.pathname !== '/analise') {
                    e.preventDefault();
                    window.location.href = '/analise';
                }
                break;
            case '5':
                if (window.location.pathname !== '/relatorios') {
                    e.preventDefault();
                    window.location.href = '/relatorios';
                }
                break;
        }
    }
});

// Configuração inicial
document.addEventListener('DOMContentLoaded', function() {
    // Adicionar classes de animação
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
    
    // Configurar tooltips do Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});