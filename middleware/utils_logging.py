import logging
import os
from django.conf import settings


def get_logger(name):
    """Get configured logger"""
    return logging.getLogger(f'apps.{name}')


def log_user_action(user, action, details=None):
    """Log user actions for audit"""
    logger = get_logger('audit')
    logger.info(f'User {user.username} performed {action}', extra={
        'user_id': user.id,
        'action': action,
        'details': details or {},
        'ip_address': getattr(user, 'ip_address', None)
    })


def log_performance(func_name, duration, details=None):
    """Log performance metrics"""
    logger = get_logger('performance')
    logger.info(f'Function {func_name} took {duration:.2f}s', extra={
        'function': func_name,
        'duration': duration,
        'details': details or {}
    })


class LogContext:
    """Context manager for logging"""

    def __init__(self, logger_name, action):
        self.logger = get_logger(logger_name)
        self.action = action

    def __enter__(self):
        self.logger.info(f'Starting {self.action}')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.logger.error(f'Error in {self.action}: {exc_val}')
        else:
            self.logger.info(f'Completed {self.action}')