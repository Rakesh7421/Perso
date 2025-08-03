// Main JavaScript file for LinkedIn Post Scheduler

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (!alert.querySelector('.btn-close')) {
            setTimeout(() => {
                alert.classList.remove('show');
                setTimeout(() => alert.remove(), 150);
            }, 5000);
        }
    });

    // Character counter for textareas
    const textareas = document.querySelectorAll('textarea[maxlength]');
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        const charCount = document.getElementById('charCount');
        
        if (charCount) {
            updateCharacterCount(textarea, charCount, maxLength);
            textarea.addEventListener('input', () => {
                updateCharacterCount(textarea, charCount, maxLength);
            });
        }
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Auto-save form data to localStorage
    const forms = document.querySelectorAll('form[data-autosave]');
    forms.forEach(form => {
        setupAutoSave(form);
    });

    // Initialize date/time inputs with current values
    initializeDateTimeInputs();

    // Setup keyboard shortcuts
    setupKeyboardShortcuts();
});

/**
 * Update character count display
 */
function updateCharacterCount(textarea, counterElement, maxLength) {
    const currentLength = textarea.value.length;
    counterElement.textContent = currentLength;
    
    // Update styling based on character count
    const percentage = (currentLength / maxLength) * 100;
    
    if (percentage >= 90) {
        counterElement.className = 'text-danger fw-bold';
    } else if (percentage >= 75) {
        counterElement.className = 'text-warning fw-bold';
    } else {
        counterElement.className = 'text-muted';
    }
    
    // Visual indicator on textarea
    if (percentage >= 100) {
        textarea.classList.add('border-danger');
    } else if (percentage >= 90) {
        textarea.classList.add('border-warning');
        textarea.classList.remove('border-danger');
    } else {
        textarea.classList.remove('border-warning', 'border-danger');
    }
}

/**
 * Setup auto-save functionality
 */
function setupAutoSave(form) {
    const formId = form.id || 'auto-save-form';
    const saveKey = `autosave_${formId}`;
    
    // Load saved data
    const savedData = localStorage.getItem(saveKey);
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            Object.keys(data).forEach(key => {
                const element = form.querySelector(`[name="${key}"]`);
                if (element && element.type !== 'file') {
                    element.value = data[key];
                }
            });
        } catch (e) {
            console.error('Error loading auto-saved data:', e);
        }
    }
    
    // Save data on input
    const inputs = form.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        if (input.type !== 'file' && input.type !== 'submit') {
            input.addEventListener('input', debounce(() => {
                saveFormData(form, saveKey);
            }, 1000));
        }
    });
    
    // Clear saved data on successful submit
    form.addEventListener('submit', () => {
        localStorage.removeItem(saveKey);
    });
}

/**
 * Save form data to localStorage
 */
function saveFormData(form, key) {
    const data = {};
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        if (input.name && input.type !== 'file' && input.type !== 'submit') {
            data[input.name] = input.value;
        }
    });
    
    localStorage.setItem(key, JSON.stringify(data));
}

/**
 * Debounce function to limit function calls
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Initialize date/time inputs with appropriate defaults
 */
function initializeDateTimeInputs() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const timeInputs = document.querySelectorAll('input[type="time"]');
    
    dateInputs.forEach(input => {
        if (!input.value) {
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            input.value = tomorrow.toISOString().split('T')[0];
        }
        
        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        input.setAttribute('min', today);
    });
    
    timeInputs.forEach(input => {
        if (!input.value) {
            const now = new Date();
            now.setHours(now.getHours() + 1);
            const hours = now.getHours().toString().padStart(2, '0');
            const minutes = now.getMinutes().toString().padStart(2, '0');
            input.value = `${hours}:${minutes}`;
        }
    });
}

/**
 * Setup keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl+S to save form
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            const form = document.querySelector('form');
            if (form) {
                const saveButton = form.querySelector('button[type="submit"]');
                if (saveButton) {
                    saveButton.click();
                }
            }
        }
        
        // Ctrl+N for new post
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            const newPostLink = document.querySelector('a[href*="create-post"]');
            if (newPostLink) {
                window.location.href = newPostLink.href;
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modal = bootstrap.Modal.getInstance(openModal);
                if (modal) {
                    modal.hide();
                }
            }
        }
    });
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Show loading state on buttons
 */
function showLoading(button, loadingText = 'Loading...') {
    const originalText = button.innerHTML;
    button.innerHTML = `<i class="bi bi-hourglass-split me-1 loading"></i>${loadingText}`;
    button.disabled = true;
    
    return function hideLoading() {
        button.innerHTML = originalText;
        button.disabled = false;
    };
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 3000) {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div class="toast" id="${toastId}" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="bi bi-${getToastIcon(type)} me-2 text-${type}"></i>
                <strong class="me-auto">LinkedIn Scheduler</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: duration });
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

/**
 * Create toast container if it doesn't exist
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

/**
 * Get appropriate icon for toast type
 */
function getToastIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Validate form before submission
 */
function validateForm(form) {
    const errors = [];
    
    // Check required fields
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            errors.push(`${field.labels[0]?.textContent || field.name} is required`);
            field.classList.add('is-invalid');
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    // Check specific field types
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        if (field.value && !isValidEmail(field.value)) {
            errors.push('Please enter a valid email address');
            field.classList.add('is-invalid');
        }
    });
    
    const dateFields = form.querySelectorAll('input[type="date"]');
    dateFields.forEach(field => {
        if (field.value && new Date(field.value) < new Date()) {
            errors.push('Date must be in the future');
            field.classList.add('is-invalid');
        }
    });
    
    return errors;
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Copy text to clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard!', 'success');
    } catch (err) {
        console.error('Failed to copy text: ', err);
        showToast('Failed to copy text', 'danger');
    }
}

/**
 * Export data as CSV
 */
function exportToCSV(data, filename) {
    if (!data || data.length === 0) {
        showToast('No data to export', 'warning');
        return;
    }
    
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => 
            headers.map(header => {
                const value = row[header] || '';
                return typeof value === 'string' && value.includes(',') 
                    ? `"${value.replace(/"/g, '""')}"` 
                    : value;
            }).join(',')
        )
    ].join('\n');
    
    downloadFile(csvContent, filename, 'text/csv');
}

/**
 * Download file
 */
function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
}

// Global utility functions
window.schedulerUtils = {
    formatDate,
    formatFileSize,
    showLoading,
    showToast,
    validateForm,
    copyToClipboard,
    exportToCSV,
    downloadFile
};
