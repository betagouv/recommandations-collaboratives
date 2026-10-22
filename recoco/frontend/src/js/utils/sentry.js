import * as Sentry from '@sentry/browser';

const configElement = document.getElementById('sentryConfig');

if (configElement) {
    const config = JSON.parse(configElement.textContent);

    Sentry.init({
        dsn: config.dsn,
        environment: config.environment,
        release: config.release,
        tracesSampleRate: config.tracesSampleRate,
        integrations:
            config.tracesSampleRate > 0 ? [Sentry.browserTracingIntegration()] : [],
        ignoreErrors: [
            'ResizeObserver loop limit exceeded',
            'ResizeObserver loop completed with undelivered notifications',
        ],
        denyUrls: [/extensions\//i, /^chrome:\/\//i, /^moz-extension:\/\//i],
    });

    if (config.userId) {
        Sentry.setUser({ id: config.userId });
    }
}
