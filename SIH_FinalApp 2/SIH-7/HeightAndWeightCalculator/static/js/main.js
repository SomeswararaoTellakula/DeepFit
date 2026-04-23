// Particle System
class ParticleSystem {
    constructor() {
        this.particles = [];
        this.container = document.getElementById('particles-js');
        this.init();
        this.animate();
    }

    init() {
        if (!this.container) return;
        
        for (let i = 0; i < 50; i++) {
            this.createParticle();
        }
    }

    createParticle() {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        // Random properties
        const size = Math.random() * 5 + 2;
        const posX = Math.random() * 100;
        const posY = Math.random() * 100;
        const opacity = Math.random() * 0.5 + 0.2;
        const duration = Math.random() * 2 + 2;
        const delay = Math.random() * 2;

        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${posX}%`;
        particle.style.top = `${posY}%`;
        particle.style.opacity = opacity;
        particle.style.animationDuration = `${duration}s`;
        particle.style.animationDelay = `${delay}s`;

        this.container.appendChild(particle);
        this.particles.push({
            element: particle,
            x: posX,
            y: posY,
            speed: Math.random() * 0.5 + 0.2,
            size: size
        });
    }

    animate() {
        if (!this.container) return;

        this.particles.forEach(particle => {
            particle.y -= particle.speed;
            if (particle.y < -10) {
                particle.y = 110;
            }
            particle.element.style.top = `${particle.y}%`;
        });

        requestAnimationFrame(() => this.animate());
    }
}

// UI Animations
class UIAnimator {
    static initializeAnimations() {
        // Add animation classes to elements
        document.querySelectorAll('.animate-on-scroll').forEach(element => {
            this.handleScrollAnimation(element);
        });

        // Handle scroll animations
        window.addEventListener('scroll', () => {
            document.querySelectorAll('.animate-on-scroll').forEach(element => {
                this.handleScrollAnimation(element);
            });
        });

        // Initialize hover effects
        this.initializeHoverEffects();
    }

    static handleScrollAnimation(element) {
        const elementTop = element.getBoundingClientRect().top;
        const windowHeight = window.innerHeight;

        if (elementTop < windowHeight * 0.75) {
            element.classList.add('animate__animated', 'animate__fadeInUp');
        }
    }

    static initializeHoverEffects() {
        // Card hover effects
        document.querySelectorAll('.card.glass').forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px)';
                this.style.boxShadow = '0 12px 40px 0 rgba(0, 0, 0, 0.5)';
            });

            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = 'var(--box-shadow)';
            });
        });

        // Button hover effects
        document.querySelectorAll('.btn-primary').forEach(button => {
            button.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.05)';
            });

            button.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
            });
        });
    }
}

// Form Validation
class FormValidator {
    static validate(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input, select, textarea');

        // Remove existing error messages
        form.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
        inputs.forEach(input => input.classList.remove('is-invalid'));

        inputs.forEach(input => {
            if (input.hasAttribute('required') && !input.value.trim()) {
                this.showError(input, 'This field is required');
                isValid = false;
            }

            if (input.type === 'email' && input.value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(input.value)) {
                    this.showError(input, 'Please enter a valid email');
                    isValid = false;
                }
            }

            if (input.type === 'password' && input.value && input.value.length < 6) {
                this.showError(input, 'Password must be at least 6 characters');
                isValid = false;
            }
        });

        return isValid;
    }

    static showError(input, message) {
        input.classList.add('is-invalid');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback animate__animated animate__fadeIn';
        errorDiv.textContent = message;
        input.parentNode.appendChild(errorDiv);
    }
}

// Flash Messages
class FlashMessage {
    static show(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show animate__animated animate__slideInRight`;
        alertDiv.innerHTML = `
            <i class="fas fa-info-circle"></i> ${message}
            <button type="button" class="close" data-dismiss="alert">
                <span>&times;</span>
            </button>
        `;

        const container = document.querySelector('.flash-messages');
        if (container) {
            container.appendChild(alertDiv);
            setTimeout(() => {
                alertDiv.classList.add('animate__slideOutRight');
                setTimeout(() => {
                    alertDiv.remove();
                }, 500);
            }, 5000);
        }
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize UI components
    new ParticleSystem();
    UIAnimator.initializeAnimations();

    // Form validation
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!FormValidator.validate(this)) {
                e.preventDefault();
            }
        });
    });

    // Initialize Bootstrap components
    $('[data-toggle="tooltip"]').tooltip();
    $('[data-toggle="popover"]').popover();

    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
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

    // Add animation delays to nav items
    document.querySelectorAll('.nav-link').forEach((link, index) => {
        link.style.animationDelay = `${index * 0.1}s`;
    });
});
