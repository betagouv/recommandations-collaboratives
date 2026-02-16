import Alpine from 'alpinejs';

const CRISP_POPUP_STORAGE_KEY = 'crispPopupViewCount';
const MAX_POPUP_VIEWS = 3;

/**
 * Crisp Chat Controller Component
 *
 * Hides the Crisp availability tooltip after it has been shown MAX_POPUP_VIEWS times.
 * Uses Crisp's native API to prevent the tooltip from appearing.
 */
export default function Crisp() {
  return {
    init() {
      // Force display on mobile
      window.$crisp = window.$crisp || [];
      window.$crisp.push(['config', 'hide:on:mobile', [false]]);

      const viewCount = parseInt(
        localStorage.getItem(CRISP_POPUP_STORAGE_KEY) || '0',
        10
      );
      if (viewCount >= MAX_POPUP_VIEWS) {
        this.hideCrispPopup();
      } else {
        setTimeout(() => {
          const crispPopup = document.querySelector('.cc-1442g');
          if (crispPopup) {
            localStorage.setItem(
              CRISP_POPUP_STORAGE_KEY,
              (viewCount + 1).toString()
            );
          }
        }, 3000);
      }

      this.$watch('$store.crisp.isPopupOpen', (isOpen) => {
        if (isOpen) {
          this.hideCrispPopup();
        }
      });
    },

    hideCrispPopup() {
      // Disable tooltip before Crisp loads
      window.$crisp = window.$crisp || [];
      window.$crisp.push(['config', 'availability:tooltip', [false]]);
    },
  };
}

Alpine.data('Crisp', Crisp);
