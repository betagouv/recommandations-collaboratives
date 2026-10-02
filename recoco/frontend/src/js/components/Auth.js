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
     * happens in a top-level popup.
     *
     * Browsers partitioning third-party cookies (Firefox, Safari, Chrome
     * soon) keep the iframe session apart from the popup one: the iframe only
     * sees it once the Storage Access API grants access, which needs a user
     * gesture after Recoco has been visited top-level, i.e. after the popup.
     * Hence the "continue" button. Elsewhere, polling the session status is
     * enough to reload the iframe once logged in.
     */
    proconnectPopup(el) {
      const { popupUrl, statusUrl, nextUrl } = el.dataset;

      // no storage access request here: window.open consumes the user
      // activation it would need, and Recoco has not been visited top-level yet
      window.open(popupUrl, 'proconnect', 'popup,width=600,height=750');

      this.proconnectPending = true;
      this.pollProconnectStatus(statusUrl, nextUrl, Date.now());
    },
    async requestStorageAccess() {
      if (!document.requestStorageAccess) return;
      try {
        // called first thing in the click handler to keep the user
        // activation; resolves right away when access is already granted
        await document.requestStorageAccess();
      } catch {
        // denied by the user or the browser: reloading will show the login
        // page again
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
    // once logged in through the popup, this click is the user gesture the
    // Storage Access API needs to share the session with the iframe
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
