import Alpine from 'alpinejs';
import * as Sentry from '@sentry/browser';

Alpine.data('SentryConfig', (currentUserEmail) => ({
  init() {
    Sentry.setUser({
      email: currentUserEmail,
    });
  },
}));
