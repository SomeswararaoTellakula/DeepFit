import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

# Create logs directory if it doesn't exist
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

def setup_logging(app_name='app'):
    """Set up application logging with rotating file handler"""
    
    # Create formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # Create rotating file handler
    log_file = os.path.join(log_dir, f'{app_name}_{datetime.now().strftime("%Y%m")}.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1024 * 1024,  # 1MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Create application logger
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.INFO)
    
    return logger

def log_error(error, context=None):
    """Log an error with optional context information"""
    logger = logging.getLogger()
    
    error_msg = f"Error: {str(error)}"
    if context:
        error_msg = f"{error_msg}\nContext: {context}"
    
    logger.error(error_msg, exc_info=True)
    
def log_warning(message, context=None):
    """Log a warning with optional context"""
    logger = logging.getLogger()
    
    warning_msg = f"Warning: {message}"
    if context:
        warning_msg = f"{warning_msg}\nContext: {context}"
    
    logger.warning(warning_msg)
    
def log_info(message):
    """Log an informational message"""
    logger = logging.getLogger()
    logger.info(message)