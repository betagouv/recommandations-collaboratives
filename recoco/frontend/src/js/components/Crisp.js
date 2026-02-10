import Alpine from 'alpinejs';

const CRISP_POPUP_STORAGE_KEY = 'crispPopupViewCount';
const MAX_POPUP_VIEWS = 3;

/**
 * Crisp Chat Controller Component
 *
 * Watches the crisp store to hide the Crisp "little" popup
 * when another modal or popup is open.
 * Also hides the popup after it has been shown MAX_POPUP_VIEWS times.
 */
export default function Crisp() {
  return {
    init() {
      setTimeout(() => {
        const crispPopup = document.querySelector('.cc-1442g');
        if (crispPopup) {
          const viewCount = parseInt(
            localStorage.getItem(CRISP_POPUP_STORAGE_KEY) || '0',
            10
          );
          if (viewCount >= MAX_POPUP_VIEWS) {
            this.hideCrispPopup();
          } else {
            localStorage.setItem(
              CRISP_POPUP_STORAGE_KEY,
              (viewCount + 1).toString()
            );
          }
        }
      }, 3000);

      this.$watch('$store.crisp.isPopupOpen', (isOpen) => {
        if (isOpen) {
          this.hideCrispPopup();
        }
      });
    },

    hideCrispPopup() {
      const crispPopup = document.querySelector('.cc-1442g');
      if (crispPopup) {
        crispPopup.style.setProperty('display', 'none', 'important');
      }
    },
  };
}

Alpine.data('Crisp', Crisp);
