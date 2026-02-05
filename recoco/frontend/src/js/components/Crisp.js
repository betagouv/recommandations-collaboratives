import Alpine from 'alpinejs';

/**
 * Crisp Chat Controller Component
 *
 * Watches the crisp store to hide the Crisp popup (aria-live="polite")
 * when another modal or popup is open.
 */
export default function Crisp() {
  return {
    init() {
      this.hideCrispPopup();

      this.$watch('$store.crisp.isPopupOpen', (isOpen) => {
        if (isOpen) {
          this.hideCrispPopup();
        }
      });
    },

    hideCrispPopup() {
      const crispPopup = document.querySelector('[aria-live="polite"]');
      if (crispPopup) {
        crispPopup.style.display = 'none';
      }
    },
  };
}

Alpine.data('Crisp', Crisp);
