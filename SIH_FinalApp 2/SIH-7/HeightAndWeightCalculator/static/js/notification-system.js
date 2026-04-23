// Enhanced notification system for better user experience

class NotificationSystem {
    constructor() {
        this.container = this.createContainer();
        document.body.appendChild(this.container);
    }

    createContainer() {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            max-width: 400px;
        `;
        return container;
    }

    show(message, type = 'info', duration = 5000) {
        const notification = this.createNotification(message, type);
        this.container.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
            notification.style.opacity = '1';
        }, 100);

        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                this.remove(notification);
            }, duration);
        }

        return notification;
    }

    createNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        notification.innerHTML = `
            <div class="notification-content">
                <i class="${icons[type] || icons.info}"></i>
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="notificationSystem.remove(this.parentElement.parentElement)">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        notification.style.cssText = `
            background: ${this.getBackgroundColor(type)};
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            margin-bottom: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            transform: translateX(100%);
            opacity: 0;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        `;

        return notification;
    }

    getBackgroundColor(type) {
        const colors = {
            success: 'linear-gradient(135deg, #28a745, #20c997)',
            error: 'linear-gradient(135deg, #dc3545, #e74c3c)',
            warning: 'linear-gradient(135deg, #ffc107, #fd7e14)',
            info: 'linear-gradient(135deg, #17a2b8, #007bff)'
        };
        return colors[type] || colors.info;
    }

    remove(notification) {
        notification.style.transform = 'translateX(100%)';
        notification.style.opacity = '0';
        setTimeout(() => {
            if (notification.parentElement) {
                notification.parentElement.removeChild(notification);
            }
        }, 300);
    }

    showProgress(message, steps = []) {
        const notification = this.createProgressNotification(message, steps);
        this.container.appendChild(notification);

        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
            notification.style.opacity = '1';
        }, 100);

        return notification;
    }

    createProgressNotification(message, steps) {
        const notification = document.createElement('div');
        notification.className = 'notification notification-progress';
        
        let stepsHtml = '';
        steps.forEach((step, index) => {
            stepsHtml += `
                <div class="progress-step" data-step="${index}">
                    <i class="fas fa-circle"></i>
                    <span>${step}</span>
                </div>
            `;
        });

        notification.innerHTML = `
            <div class="notification-content">
                <div class="progress-header">
                    <i class="fas fa-cog fa-spin"></i>
                    <span class="notification-message">${message}</span>
                </div>
                <div class="progress-steps">
                    ${stepsHtml}
                </div>
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
            </div>
        `;

        notification.style.cssText = `
            background: linear-gradient(135deg, #4facfe, #00f2fe);
            color: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 10px;
            box-shadow: 0 8px 30px rgba(79, 172, 254, 0.3);
            transform: translateX(100%);
            opacity: 0;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            min-width: 350px;
        `;

        return notification;
    }

    updateProgress(notification, currentStep, totalSteps) {
        const progressFill = notification.querySelector('.progress-fill');
        const steps = notification.querySelectorAll('.progress-step');
        
        // Update progress bar
        const percentage = (currentStep / totalSteps) * 100;
        progressFill.style.width = percentage + '%';
        
        // Update step indicators
        steps.forEach((step, index) => {
            if (index < currentStep) {
                step.classList.add('completed');
                step.querySelector('i').className = 'fas fa-check-circle';
            } else if (index === currentStep) {
                step.classList.add('active');
                step.querySelector('i').className = 'fas fa-circle-notch fa-spin';
            }
        });
    }
}

// Initialize global notification system
const notificationSystem = new NotificationSystem();

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
    .notification-content {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .notification-message {
        flex: 1;
        font-weight: 500;
    }

    .notification-close {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        padding: 5px;
        border-radius: 50%;
        transition: background 0.2s ease;
    }

    .notification-close:hover {
        background: rgba(255,255,255,0.2);
    }

    .progress-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 15px;
    }

    .progress-steps {
        margin-bottom: 15px;
    }

    .progress-step {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
        opacity: 0.6;
        transition: opacity 0.3s ease;
    }

    .progress-step.active {
        opacity: 1;
        font-weight: 600;
    }

    .progress-step.completed {
        opacity: 0.8;
    }

    .progress-step.completed i {
        color: #28a745;
    }

    .progress-bar {
        width: 100%;
        height: 4px;
        background: rgba(255,255,255,0.3);
        border-radius: 2px;
        overflow: hidden;
    }

    .progress-fill {
        height: 100%;
        background: white;
        width: 0%;
        transition: width 0.3s ease;
        border-radius: 2px;
    }
`;
document.head.appendChild(style);