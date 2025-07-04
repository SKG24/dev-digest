/* File: static/js/main.js */
document.addEventListener('DOMContentLoaded', function() {
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.style.borderColor = 'var(--error-red)';
                    isValid = false;
                } else {
                    field.style.borderColor = 'var(--border-gray)';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
    
    // Auto-hide success messages
    const successMessages = document.querySelectorAll('.success-message');
    successMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 3000);
    });
    
    // GitHub username validation
    const githubInput = document.querySelector('input[name="github_username"]');
    if (githubInput) {
        githubInput.addEventListener('blur', function() {
            const username = this.value.trim();
            if (username && !/^[a-zA-Z0-9]([a-zA-Z0-9]|-){0,38}$/.test(username)) {
                this.style.borderColor = 'var(--error-red)';
                this.setCustomValidity('Invalid GitHub username format');
            } else {
                this.style.borderColor = 'var(--border-gray)';
                this.setCustomValidity('');
            }
        });
    }
    
    // Email validation
    const emailInput = document.querySelector('input[name="email"]');
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            const email = this.value.trim();
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (email && !emailRegex.test(email)) {
                this.style.borderColor = 'var(--error-red)';
                this.setCustomValidity('Invalid email format');
            } else {
                this.style.borderColor = 'var(--border-gray)';
                this.setCustomValidity('');
            }
        });
    }
});