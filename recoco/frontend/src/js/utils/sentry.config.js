import * as Sentry from '@sentry/browser';

Sentry.init({
  dsn: 'https://5b872cee93efddce4396cc52605838c1@sentry.incubateur.net/178',
  integrations: [Sentry.replayIntegration()],
  // Session Replay
  replaysSessionSampleRate: 0.1, // This sets the sample rate at 10%. You may want to change it to 100% while in development and then sample at a lower rate in production.
  replaysOnErrorSampleRate: 1.0, // If you're not already sampling the entire session, change the sample rate to 100% when sampling sessions where errors occur.
});
