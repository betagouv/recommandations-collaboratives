import * as Sentry from '@sentry/browser';

const configElement = document.getElementById('sentryConfig');

if (configElement) {
  const config = JSON.parse(configElement.textContent);

  Sentry.init({
    dsn: config.dsn,
    release: config.release,
    denyUrls: [/extensions\//i, /^chrome:\/\//i, /^moz-extension:\/\//i],
  });

  if (config.userId) {
    Sentry.setUser({ id: config.userId });
  }
}
