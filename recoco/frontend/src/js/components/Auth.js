import Alpine from 'alpinejs';
import { escapeHtml } from '../utils/escapeHTML';

function Auth() {
  return {
    initLogin() {
      const loginInput = document.getElementById('id_login');
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
    initResetPassword() {
      const url = new URL(window.location.href);
      const urlHash = url.hash.replace('#', '');

      const loginInput = document.getElementById('id_email');

      if (urlHash && urlHash.length > 0) loginInput.value = urlHash;
    },
  };
}

Alpine.data('Auth', Auth);
