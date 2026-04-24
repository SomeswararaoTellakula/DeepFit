class SitupsTracker {
    constructor() {
        this.isRunning = false;
        this.statsInterval = null;
        this.timerInterval = null;
        this.timeRemaining = 180; // 3 minutes in seconds
        this.totalTime = 180;
        this.startTime = null;
        this.endTime = null;
        this.timerCompleted = false;
        this.isVerified = false;
        this.initializeElements();
        this.bindEvents();
        this.initializeVerificationCamera();
    }

    initializeElements() {
        this.startBtn = document.getElementById('start-btn');
        this.verifyBtn = document.getElementById('verify-btn');
        this.stopBtn = document.getElementById('stop-btn');
        this.resetBtn = document.getElementById('reset-btn');
        this.submitBtn = document.getElementById('submit-btn');
        this.previewBtn = document.getElementById('preview-btn');
        this.videoFeed = document.getElementById('video-feed');
        this.previewVideo = document.getElementById('preview-video');
        this.verifyVideo = document.getElementById('verify-video');
        this.placeholder = document.getElementById('placeholder');
        this.repsCount = document.getElementById('reps-count');
        this.formProgress = document.getElementById('form-progress');
        this.formPercentage = document.getElementById('form-percentage');
        this.identityVerified = document.getElementById('identity-verified');
        this.feedback = document.getElementById('feedback');
        this.timerDisplay = document.getElementById('timer-display');
        this.timerProgress = document.getElementById('timer-progress');
        this.sessionStatus = document.getElementById('session-status');
    }

    bindEvents() {
        this.startBtn.addEventListener('click', () => this.startCamera());
        this.verifyBtn.addEventListener('click', () => this.verifyIdentity());
        this.stopBtn.addEventListener('click', () => this.stopCamera());
        this.previewBtn.addEventListener('click', () => this.togglePreview());
        this.resetBtn.addEventListener('click', () => this.resetCounter());
        this.submitBtn.addEventListener('click', () => this.submitResults());
    }

    async initializeVerificationCamera() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            this.verifyVideo.srcObject = stream;
            this.sessionStatus.textContent = 'Please verify identity to start';
        } catch (error) {
            console.error('Error accessing verification camera:', error);
        }
    }

    async verifyIdentity() {
        try {
            this.verifyBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verifying...';
            this.verifyBtn.disabled = true;

            const canvas = document.createElement('canvas');
            canvas.width = this.verifyVideo.videoWidth || 640;
            canvas.height = this.verifyVideo.videoHeight || 480;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(this.verifyVideo, 0, 0);
            const frameData = canvas.toDataURL('image/jpeg');

            const response = await fetch('/api/verify_user_identity', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ frame_data: frameData })
            });

            const result = await response.json();

            if (result.success && result.is_match) {
                this.isVerified = true;
                this.startBtn.disabled = false;
                if (this.identityVerified) {
                    this.identityVerified.textContent = 'YES';
                    this.identityVerified.style.color = '#4CAF50';
                }
                this.verifyBtn.innerHTML = '<i class="fas fa-check-circle"></i> Verified';
                this.sessionStatus.textContent = 'Identity verified. Ready to start.';
                
                if (this.verifyVideo.srcObject) {
                    this.verifyVideo.srcObject.getTracks().forEach(t => t.stop());
                }
            } else {
                this.isVerified = false;
                if (this.identityVerified) {
                    this.identityVerified.textContent = 'NO';
                    this.identityVerified.style.color = '#f44336';
                }
                this.verifyBtn.innerHTML = '<i class="fas fa-user-check"></i> Verify Identity';
                this.verifyBtn.disabled = false;
                alert('Identity verification failed. Please try again.');
            }
        } catch (error) {
            console.error('Verification error:', error);
            this.verifyBtn.innerHTML = '<i class="fas fa-user-check"></i> Verify Identity';
            this.verifyBtn.disabled = false;
        }
    }

    async togglePreview() {
        if (this.isPreviewing) {
            this.stopPreview();
        } else {
            await this.startPreview();
        }
    }

    async startPreview() {
        try {
            // Stop any running backend camera
            if (this.isRunning) await this.stopCamera();
            
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            this.previewVideo.srcObject = stream;
            this.previewVideo.style.display = 'block';
            this.videoFeed.style.display = 'none';
            this.placeholder.style.display = 'none';
            
            this.isPreviewing = true;
            this.previewBtn.innerHTML = '<i class="fas fa-video-slash"></i> Stop Preview';
            this.previewBtn.classList.add('btn-warning');
            this.sessionStatus.textContent = 'Preview active';
            
            return stream;
        } catch (error) {
            console.error('Error starting preview:', error);
            this.showFeedback('Camera access denied: ' + error.message, 'error');
        }
    }

    stopPreview() {
        if (this.previewVideo.srcObject) {
            this.previewVideo.srcObject.getTracks().forEach(t => t.stop());
            this.previewVideo.srcObject = null;
        }
        this.previewVideo.style.display = 'none';
        this.placeholder.style.display = 'flex';
        this.isPreviewing = false;
        this.previewBtn.innerHTML = '<i class="fas fa-video"></i> Camera Preview';
        this.previewBtn.classList.remove('btn-warning');
        this.sessionStatus.textContent = 'Preview stopped';
    }

    async startCamera() {
        try {
            // Stop browser preview if active
            if (this.isPreviewing) this.stopPreview();
            
            this.showLoading('Starting AI system...');
            
            // Add timestamp to prevent caching issues
            const response = await fetch('/situp/start_camera?' + new Date().getTime());
            const data = await response.json();
            
            if (data.status === 'success') {
                this.isRunning = true;
                // Add timestamp to video feed URL to force refresh
                this.videoFeed.src = '/situp/video_feed?' + new Date().getTime();
                this.videoFeed.style.display = 'block';
                this.placeholder.style.display = 'none';
                
                this.startBtn.disabled = true;
                this.stopBtn.disabled = false;
                
                this.startTimer();
                this.startStatsUpdate();
                this.showFeedback('Camera started! Begin your situps.', 'success');
            } else {
                this.showFeedback('Failed to start camera: ' + data.message, 'error');
            }
        } catch (error) {
            this.showFeedback('Error starting camera: ' + error.message, 'error');
        }
    }

    async stopCamera() {
        try {
            await fetch('/situp/stop_camera');
            
            this.isRunning = false;
            this.videoFeed.style.display = 'none';
            this.placeholder.style.display = 'flex';
            this.videoFeed.src = '';
            
            this.startBtn.disabled = false;
            this.stopBtn.disabled = true;
            
            this.stopTimer();
            this.stopStatsUpdate();
            this.showFeedback('Camera stopped.', 'info');
        } catch (error) {
            this.isRunning = false;
            this.videoFeed.style.display = 'none';
            this.placeholder.style.display = 'flex';
            this.startBtn.disabled = false;
            this.stopBtn.disabled = true;
            this.stopStatsUpdate();
        }
    }

    async resetCounter() {
        try {
            // Stop camera first if running
            if (this.isRunning) {
                await this.stopCamera();
            }
            
            const response = await fetch('/situp/reset_counter');
            const data = await response.json();
            
            if (data.status === 'success') {
                // Reset UI state
                this.isRunning = false;
                this.videoFeed.style.display = 'none';
                this.placeholder.style.display = 'flex';
                this.videoFeed.src = '';
                
                this.startBtn.disabled = false;
                this.stopBtn.disabled = true;
                
                this.stopStatsUpdate();
                this.resetTimer();
                
                // Reset stats display
                this.updateStats({
                    reps: 0,
                    feedback: 'Get Ready',
                    form_percentage: 0
                });
                
                this.showFeedback('Counter reset! Ready for new session.', 'success');
            } else {
                this.showFeedback('Error resetting: ' + data.message, 'error');
            }
        } catch (error) {
            this.showFeedback('Error resetting counter: ' + error.message, 'error');
        }
    }

    startStatsUpdate() {
        this.statsInterval = setInterval(async () => {
            if (this.isRunning) {
                try {
                    const response = await fetch('/situp/get_stats');
                    const stats = await response.json();
                    this.updateStats(stats);
                } catch (error) {
                    console.error('Error fetching stats:', error);
                }
            }
        }, 500);
    }

    stopStatsUpdate() {
        if (this.statsInterval) {
            clearInterval(this.statsInterval);
            this.statsInterval = null;
        }
    }

    updateStats(stats) {
        // Update reps count with animation
        if (parseInt(this.repsCount.textContent) !== stats.reps) {
            this.animateNumber(this.repsCount, stats.reps);
        }
        
        // Update form percentage and progress bar with smooth transition
        const formPercentage = stats.form_percentage || 0;
        this.formPercentage.textContent = formPercentage + '%';
        this.formProgress.style.width = formPercentage + '%';
        
        // Update progress bar color based on form quality
        if (formPercentage >= 80) {
            this.formProgress.style.backgroundColor = '#4CAF50'; // Green
        } else if (formPercentage >= 60) {
            this.formProgress.style.backgroundColor = '#FF9800'; // Orange
        } else {
            this.formProgress.style.backgroundColor = '#f44336'; // Red
        }
        
        // Update feedback with color coding
        this.feedback.textContent = stats.feedback || 'Get Ready';
        this.updateFeedbackColor(stats.feedback || 'Get Ready');
    }

    updateFeedbackColor(feedback) {
        this.feedback.className = 'feedback';
        
        if (feedback.includes('Good') || feedback.includes('Perfect') || feedback.includes('Great')) {
            this.feedback.classList.add('success');
        } else if (feedback.includes('Keep') || feedback.includes('Go')) {
            this.feedback.classList.add('warning');
        } else if (feedback.includes('No pose') || feedback.includes('Position')) {
            this.feedback.classList.add('error');
        }
    }

    animateNumber(element, targetValue) {
        const currentValue = parseInt(element.textContent) || 0;
        const increment = targetValue > currentValue ? 1 : -1;
        const duration = 300;
        const steps = Math.abs(targetValue - currentValue);
        const stepDuration = duration / steps;

        let current = currentValue;
        const timer = setInterval(() => {
            current += increment;
            element.textContent = current;
            
            if (current === targetValue) {
                clearInterval(timer);
                // Add celebration effect for new reps
                if (targetValue > 0 && increment > 0) {
                    this.celebrateRep(element);
                }
            }
        }, stepDuration);
    }

    celebrateRep(element) {
        element.classList.add('animate');
        
        // Add celebration effect
        const celebration = document.createElement('div');
        celebration.textContent = '🎉';
        celebration.style.cssText = `
            position: absolute;
            font-size: 24px;
            animation: celebrate 1s ease-out;
            pointer-events: none;
        `;
        
        element.parentNode.appendChild(celebration);
        
        setTimeout(() => {
            element.classList.remove('animate');
            if (celebration.parentNode) {
                celebration.parentNode.removeChild(celebration);
            }
        }, 1000);
    }

    showLoading(message) {
        this.feedback.textContent = message;
        this.feedback.style.color = '#2196F3';
    }

    showFeedback(message, type) {
        const colors = {
            success: '#4CAF50',
            error: '#f44336',
            info: '#2196F3',
            warning: '#ff9800'
        };
        
        // Only show temporary feedback for non-running states
        if (!this.isRunning || type === 'error') {
            const originalFeedback = this.feedback.textContent;
            const originalColor = this.feedback.style.color;
            
            this.feedback.textContent = message;
            this.feedback.style.color = colors[type] || '#666';
            
            // Restore original feedback after 3 seconds
            setTimeout(() => {
                if (!this.isRunning) {
                    this.feedback.textContent = 'Get Ready';
                    this.feedback.style.color = '#666';
                }
            }, 3000);
        }
    }

    startTimer() {
        this.startTime = new Date();
        this.timeRemaining = 180;
        this.timerCompleted = false;
        this.updateTimerDisplay();
        
        this.timerInterval = setInterval(() => {
            this.timeRemaining--;
            this.updateTimerDisplay();
            
            if (this.timeRemaining <= 0) {
                this.onTimerComplete();
            }
        }, 1000);
        
        this.sessionStatus.textContent = 'Session in progress';
    }

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        this.endTime = new Date();
        this.sessionStatus.textContent = 'Session paused';
    }

    resetTimer() {
        this.stopTimer();
        this.timeRemaining = 180;
        this.totalTime = 180;
        this.startTime = null;
        this.endTime = null;
        this.timerCompleted = false;
        this.updateTimerDisplay();
        this.sessionStatus.textContent = 'Ready to start';
    }

    updateTimerDisplay() {
        const minutes = Math.floor(this.timeRemaining / 60);
        const seconds = this.timeRemaining % 60;
        this.timerDisplay.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        // Update progress bar
        const progress = ((this.totalTime - this.timeRemaining) / this.totalTime) * 100;
        this.timerProgress.style.width = progress + '%';
        
        // Change color based on time remaining
        if (this.timeRemaining <= 30) {
            this.timerDisplay.style.color = '#f44336'; // Red
        } else if (this.timeRemaining <= 60) {
            this.timerDisplay.style.color = '#ff9800'; // Orange
        } else {
            this.timerDisplay.style.color = '#2196F3'; // Blue
        }
    }

    onTimerComplete() {
        this.stopTimer();
        this.timerCompleted = true;
        this.timerDisplay.textContent = '0:00';
        this.timerProgress.style.width = '100%';
        this.sessionStatus.textContent = 'Time completed!';
        
        // Show popup
        this.showTimeCompletedPopup();
    }

    showTimeCompletedPopup() {
        const popup = document.createElement('div');
        popup.className = 'popup-overlay';
        popup.innerHTML = `
            <div class="popup-content">
                <div class="popup-icon">⏰</div>
                <h3>Time Completed!</h3>
                <p>Your 3-minute session is complete. Please click Submit to save your results.</p>
                <button onclick="this.parentElement.parentElement.remove()" class="btn btn-primary">OK</button>
            </div>
        `;
        document.body.appendChild(popup);
    }

    async submitResults() {
        try {
            // Get current stats
            const response = await fetch('/situp/get_stats');
            const stats = await response.json();
            
            const repsCompleted = stats.reps || 0;
            const formQuality = stats.form_percentage || 0;
            
            // Calculate timer time
            let timerTime;
            if (this.timerCompleted) {
                timerTime = '3:00';
            } else if (this.startTime && this.endTime) {
                const duration = Math.floor((this.endTime - this.startTime) / 1000);
                const minutes = Math.floor(duration / 60);
                const seconds = duration % 60;
                timerTime = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            } else {
                const elapsed = this.totalTime - this.timeRemaining;
                const minutes = Math.floor(elapsed / 60);
                const seconds = elapsed % 60;
                timerTime = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            }
            
            // Submit to backend
            const submitResponse = await fetch('/api/submit_situp_result', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    reps_completed: repsCompleted,
                    form_quality: formQuality,
                    timer_time: timerTime
                })
            });
            
            const submitData = await submitResponse.json();
            
            if (submitData.success) {
                // Reset everything
                await this.resetCounter();
                
                // Navigate to results page
                window.location.href = `/displaysitup?reps=${repsCompleted}&form=${formQuality}&timer=${timerTime}`;
            } else {
                this.showFeedback('Error submitting results: ' + submitData.message, 'error');
            }
        } catch (error) {
            this.showFeedback('Error submitting results: ' + error.message, 'error');
        }
    }
}

// Initialize the situps tracker when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new SitupsTracker();
});

// Handle page visibility changes and cleanup
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Page is hidden, pause the camera to save resources
        console.log('Page hidden - pausing camera');
    } else {
        // Page is visible again
        console.log('Page visible');
    }
});

// Cleanup when page is about to be unloaded
window.addEventListener('beforeunload', async () => {
    try {
        // Stop camera if running
        await fetch('/situp/cleanup', { method: 'POST' });
    } catch (error) {
        console.log('Cleanup error:', error);
    }
});

// Handle page refresh/close
window.addEventListener('unload', () => {
    // Final cleanup attempt
    navigator.sendBeacon('/situp/cleanup');
});