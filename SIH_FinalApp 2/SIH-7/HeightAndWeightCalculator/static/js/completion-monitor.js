// Completion monitoring system for height and weight analysis

class CompletionMonitor {
    constructor() {
        this.isMonitoring = false;
        this.checkInterval = null;
        this.startTime = null;
        this.maxWaitTime = 300000; // 5 minutes
    }

    startMonitoring(progressNotification) {
        if (this.isMonitoring) return;
        
        this.isMonitoring = true;
        this.startTime = Date.now();
        
        console.log('Starting completion monitoring...');
        
        // Check every 3 seconds
        this.checkInterval = setInterval(() => {
            this.checkCompletion(progressNotification);
        }, 3000);
        
        // Timeout after 5 minutes
        setTimeout(() => {
            if (this.isMonitoring) {
                this.handleTimeout(progressNotification);
            }
        }, this.maxWaitTime);
    }

    async checkCompletion(progressNotification) {
        try {
            // Method 1: Check for completion status (priority method)
            try {
                const statusResponse = await fetch('/api/check_analysis_status');
                const statusResult = await statusResponse.json();
                
                if (statusResult.completed) {
                    console.log('Analysis completion detected via status check');
                    this.completeAnalysis(progressNotification);
                    return;
                }
            } catch (statusError) {
                console.log('Status check failed:', statusError);
            }
            
            // Method 2: Check for recent final estimate
            const response = await fetch('/api/get_latest_measurement');
            const result = await response.json();
            
            if (result.success && result.data) {
                const dataTimestamp = new Date(result.data.timestamp);
                const timeSinceStart = Date.now() - this.startTime;
                const timeSinceData = Date.now() - dataTimestamp.getTime();
                
                // If data is recent (within 2 minutes) and we've been monitoring for at least 20 seconds
                if (timeSinceData < 120000 && timeSinceStart > 20000) {
                    console.log('Recent final estimate detected, completing...');
                    this.completeAnalysis(progressNotification);
                    return;
                }
            }
            
        } catch (error) {
            console.log('Error checking completion:', error);
        }
    }

    completeAnalysis(progressNotification) {
        if (!this.isMonitoring) return;
        
        this.stopMonitoring();
        
        // Update progress to completion
        if (notificationSystem && progressNotification) {
            notificationSystem.updateProgress(progressNotification, 4, 5);
            
            setTimeout(() => {
                notificationSystem.updateProgress(progressNotification, 5, 5);
                notificationSystem.remove(progressNotification);
                
                // Show completion message
                notificationSystem.show('Analysis complete! Redirecting to results dashboard...', 'success');
                
                setTimeout(() => {
                    window.location.href = '/performance_dashboard';
                }, 2000);
            }, 1000);
        } else {
            // Fallback if notification system not available
            setTimeout(() => {
                window.location.href = '/performance_dashboard';
            }, 2000);
        }
    }

    handleTimeout(progressNotification) {
        console.log('Analysis monitoring timed out, redirecting anyway...');
        
        this.stopMonitoring();
        
        if (notificationSystem && progressNotification) {
            notificationSystem.remove(progressNotification);
            notificationSystem.show('Analysis timeout reached. Redirecting to dashboard...', 'warning');
        }
        
        setTimeout(() => {
            window.location.href = '/performance_dashboard';
        }, 3000);
    }

    stopMonitoring() {
        this.isMonitoring = false;
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
            this.checkInterval = null;
        }
    }
}

// Global instance
window.completionMonitor = new CompletionMonitor();