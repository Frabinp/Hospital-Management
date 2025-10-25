// Hospital Management System - Client-Side JavaScript
// This file contains all JavaScript functionality for the hospital management system
// It provides form validation, search filtering, and enhanced user interactions

// Main initialization function - runs when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all JavaScript functionality when the page loads
    initFormValidation();      // Set up form validation for all forms
    initSearchFiltering();     // Set up search filtering functionality
    initDeleteConfirmations(); // Set up delete confirmation dialogs
    initAutoHideAlerts();      // Set up auto-hide for alert messages
});

// Form Validation System - validates all forms before submission
function initFormValidation() {
    // Get all form elements on the page
    const forms = document.querySelectorAll('form');
    
    // Add submit event listener to each form
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Validate the form before allowing submission
            if (!validateForm(this)) {
                e.preventDefault();  // Prevent form submission if validation fails
            }
        });
    });
}

// Form validation function - validates individual form fields
function validateForm(form) {
    let isValid = true;  // Track overall form validity
    const requiredFields = form.querySelectorAll('[required]');  // Get all required fields
    
    // Validate all required fields
    requiredFields.forEach(field => {
        if (!field.value.trim()) {  // Check if field is empty or contains only whitespace
            showFieldError(field, 'This field is required');  // Show error message
            isValid = false;  // Mark form as invalid
        } else {
            clearFieldError(field);  // Clear any existing error messages
        }
    });
    
    // Email validation - validate all email input fields
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        if (field.value && !isValidEmail(field.value)) {  // Check if email is valid
            showFieldError(field, 'Please enter a valid email address');  // Show error message
            isValid = false;  // Mark form as invalid
        }
    });
    
    // Phone validation - validate all phone input fields
    const phoneFields = form.querySelectorAll('input[type="tel"]');
    phoneFields.forEach(field => {
        if (field.value && !isValidPhone(field.value)) {  // Check if phone is valid
            showFieldError(field, 'Please enter a valid phone number');  // Show error message
            isValid = false;  // Mark form as invalid
        }
    });
    
    return isValid;  // Return overall form validity status
}

function showFieldError(field, message) {
    clearFieldError(field);
    field.classList.add('error');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    errorDiv.style.color = '#dc3545';
    errorDiv.style.fontSize = '0.8em';
    errorDiv.style.marginTop = '5px';
    
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('error');
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPhone(phone) {
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
}

// Search Filtering
function initSearchFiltering() {
    const searchInputs = document.querySelectorAll('.search-input');
    
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const table = this.closest('.search-container').nextElementSibling;
            
            if (table && table.classList.contains('table-container')) {
                filterTable(table, searchTerm);
            }
        });
    });
}

function filterTable(tableContainer, searchTerm) {
    const table = tableContainer.querySelector('table');
    if (!table) return;
    
    const rows = table.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Delete Confirmations
function initDeleteConfirmations() {
    const deleteLinks = document.querySelectorAll('a[href*="delete"]');
    
    deleteLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const confirmMessage = this.getAttribute('onclick');
            if (!confirmMessage || !confirmMessage.includes('confirm')) {
                e.preventDefault();
                if (confirm('Are you sure you want to delete this item?')) {
                    window.location.href = this.href;
                }
            }
        });
    });
}

// Auto-hide alerts
function initAutoHideAlerts() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s';
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });
}

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Date validation for appointments
function validateAppointmentDate() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    
    dateInputs.forEach(input => {
        input.addEventListener('change', function() {
            const selectedDate = new Date(this.value);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            if (selectedDate < today) {
                showFieldError(this, 'Appointment date cannot be in the past');
            } else {
                clearFieldError(this);
            }
        });
    });
}

// Initialize date validation
document.addEventListener('DOMContentLoaded', validateAppointmentDate);

// Enhanced form interactions
function initFormEnhancements() {
    // Auto-focus first input in forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const firstInput = form.querySelector('input, select, textarea');
        if (firstInput) {
            firstInput.focus();
        }
    });
    
    // Enter key to submit forms
    const inputs = document.querySelectorAll('input, textarea');
    inputs.forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && this.type !== 'textarea') {
                const form = this.closest('form');
                if (form) {
                    form.submit();
                }
            }
        });
    });
}

// Initialize form enhancements
document.addEventListener('DOMContentLoaded', initFormEnhancements);

// Table enhancements
function initTableEnhancements() {
    const tables = document.querySelectorAll('.data-table');
    
    tables.forEach(table => {
        // Add hover effects
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.style.backgroundColor = '#f8f9fa';
            });
            
            row.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
        });
    });
}

// Initialize table enhancements
document.addEventListener('DOMContentLoaded', initTableEnhancements);
