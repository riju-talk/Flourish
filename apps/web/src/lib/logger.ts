interface LogLevel {
  ERROR: 'error';
  WARN: 'warn';
  INFO: 'info';
  DEBUG: 'debug';
}

interface LogContext {
  userId?: string;
  component?: string;
  action?: string;
  metadata?: Record<string, any>;
}

class Logger {
  private static instance: Logger;
  private logLevel: keyof LogLevel = 'info';
  private isProduction: boolean;

  constructor() {
    this.isProduction = process.env.NODE_ENV === 'production';
    this.logLevel = (process.env.REACT_APP_LOG_LEVEL as keyof LogLevel) || 'info';
  }

  static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  private shouldLog(level: keyof LogLevel): boolean {
    const levels = ['debug', 'info', 'warn', 'error'];
    const currentLevelIndex = levels.indexOf(this.logLevel);
    const messageLevelIndex = levels.indexOf(level);
    return messageLevelIndex >= currentLevelIndex;
  }

  private formatMessage(level: keyof LogLevel, message: string, context?: LogContext): string {
    const timestamp = new Date().toISOString();
    const userId = context?.userId || 'anonymous';

    return `[${timestamp}] [${level.toUpperCase()}] [${userId}] ${message}`;
  }

  private async sendToAnalytics(level: keyof LogLevel, message: string, context?: LogContext) {
    // In production, send to analytics service
    if (this.isProduction && level === 'error') {
      try {
        // Example: Send to Sentry, LogRocket, or custom analytics
        // await analytics.track('error', { message, context });
        console.log('Would send to analytics:', { level, message, context });
      } catch (error) {
        console.error('Failed to send log to analytics:', error);
      }
    }
  }

  async error(message: string, context?: LogContext): Promise<void> {
    if (!this.shouldLog('error')) return;

    const formattedMessage = this.formatMessage('error', message, context);
    console.error(formattedMessage, context);

    await this.sendToAnalytics('error', message, context);
  }

  async warn(message: string, context?: LogContext): Promise<void> {
    if (!this.shouldLog('warn')) return;

    const formattedMessage = this.formatMessage('warn', message, context);
    console.warn(formattedMessage, context);
  }

  async info(message: string, context?: LogContext): Promise<void> {
    if (!this.shouldLog('info')) return;

    const formattedMessage = this.formatMessage('info', message, context);
    console.info(formattedMessage, context);
  }

  async debug(message: string, context?: LogContext): Promise<void> {
    if (!this.shouldLog('debug')) return;

    const formattedMessage = this.formatMessage('debug', message, context);
    console.debug(formattedMessage, context);
  }

  // Analytics-specific methods
  async trackUserAction(action: string, metadata?: Record<string, any>): Promise<void> {
    const storedUser = localStorage.getItem('flourish_user');
    const user = storedUser ? JSON.parse(storedUser) : null;
    const context: LogContext = {
      userId: user?.uid,
      action,
      metadata
    };

    await this.info(`User action: ${action}`, context);

    // Send to analytics service
    if (this.isProduction) {
      try {
        // await analytics.track('user_action', { action, ...metadata, userId: user?.uid });
      } catch (error) {
        console.error('Failed to track user action:', error);
      }
    }
  }

  async trackPlantInteraction(plantId: string, action: string, metadata?: Record<string, any>): Promise<void> {
    await this.trackUserAction(`plant_${action}`, { plantId, ...metadata });
  }

  async trackChatInteraction(messageCount: number, hasImage: boolean): Promise<void> {
    await this.trackUserAction('chat_interaction', { messageCount, hasImage });
  }

  async trackError(error: Error, component?: string, metadata?: Record<string, any>): Promise<void> {
    const storedUser = localStorage.getItem('flourish_user');
    const user = storedUser ? JSON.parse(storedUser) : null;
    const context: LogContext = {
      userId: user?.uid,
      component,
      metadata: { ...metadata, errorMessage: error.message, stack: error.stack }
    };

    await this.error(`Component error in ${component || 'unknown'}: ${error.message}`, context);
  }
}

// Export singleton instance
export const logger = Logger.getInstance();

// React hook for logging in components
export const useLogger = () => {
  return {
    logError: (error: Error, component?: string, metadata?: Record<string, any>) =>
      logger.trackError(error, component, metadata),
    logUserAction: (action: string, metadata?: Record<string, any>) =>
      logger.trackUserAction(action, metadata),
    logPlantInteraction: (plantId: string, action: string, metadata?: Record<string, any>) =>
      logger.trackPlantInteraction(plantId, action, metadata),
    logChatInteraction: (messageCount: number, hasImage: boolean) =>
      logger.trackChatInteraction(messageCount, hasImage)
  };
};
