import Alpine from 'alpinejs';
import { escapeHtml } from '../utils/escapeHTML';

const PROCONNECT_POLL_INTERVAL_MS = 1500;
const PROCONNECT_POLL_TIMEOUT_MS = 5 * 60 * 1000;

function Auth() {
  return {
    proconnectPending: false,
    initLogin() {
      const loginInput = document.getElementById('id_login');
      if (!loginInput) return;
      if (loginInput.value.length > 0) {
        this.changeForgotPasswrodButtonHref(loginInput);
      }

      loginInput.addEventListener('change', (e) => {
        this.changeForgotPasswrodButtonHref(e.target);
      });
    },
    changeForgotPasswrodButtonHref(target) {
      const forgotPasswordButton = document.getElementById('forgot-password');
      const newUrlwithHash =
        forgotPasswordButton.getAttribute('href') + '#' + target.value;

      forgotPasswordButton.addEventListener('click', (e) => {
        e.preventDefault();

        location.href = escapeHtml(newUrlwithHash);
      });
    },
    /**
     * Embedded mode: ProConnect cannot run inside an iframe, so the login
     * happens in a top-level popup. The iframe then polls the session status
     * and reloads once logged in. Storage Access API lets the iframe see the
     * first-party session cookie on browsers partitioning third-party cookies.
     */
    proconnectPopup(el) {
      const { popupUrl, statusUrl, nextUrl } = el.dataset;

      // open the popup first, synchronously within the user gesture
      window.open(popupUrl, 'proconnect', 'popup,width=600,height=750');
      this.requestStorageAccess();

      this.proconnectPending = true;
      this.pollProconnectStatus(statusUrl, nextUrl, Date.now());
    },
    async requestStorageAccess() {
      if (!document.hasStorageAccess || !document.requestStorageAccess) {
        return true;
      }
      try {
        if (await document.hasStorageAccess()) return true;
        await document.requestStorageAccess();
        return true;
      } catch {
        // Safari refuses until Recoco has been visited top-level: the popup
        // does that, the user will be asked to click again afterwards
        return false;
      }
    },
    async pollProconnectStatus(statusUrl, nextUrl, startedAt) {
      // past the timeout, the "continue" button remains the way out
      if (Date.now() - startedAt > PROCONNECT_POLL_TIMEOUT_MS) return;
      try {
        const response = await fetch(statusUrl, { credentials: 'include' });
        const data = await response.json();
        if (data.authenticated) {
          window.location.href = nextUrl || window.location.href;
          return;
        }
      } catch {
        // network hiccup, keep polling
      }
      setTimeout(
        () => this.pollProconnectStatus(statusUrl, nextUrl, startedAt),
        PROCONNECT_POLL_INTERVAL_MS
      );
    },
    // when polling cannot see the session (e.g. Safari without storage access
    // granted yet), a new user gesture lets us ask for it again
    async proconnectContinue(el) {
      await this.requestStorageAccess();
      window.location.href = el.dataset.nextUrl || window.location.href;
    },
    initProconnectPopupDone() {
      // may be ignored by the browser: the page also asks to close it manually
      setTimeout(() => window.close(), 1500);
    },
    initResetPassword() {
      const url = new URL(window.location.href);
      const urlHash = url.hash.replace('#', '');

      const loginInput = document.getElementById('id_email');

      if (urlHash && urlHash.length > 0) loginInput.value = urlHash;
    },
  };
}

Alpine.data('Auth', Auth);
