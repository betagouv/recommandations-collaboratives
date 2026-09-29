import Alpine from 'alpinejs';
import { isPlural } from '../utils/isPlural';

const FIELD_SELECTOR = 'input, select, textarea';

/**
  Accordion Status Component

  Displays a single status badge in the header of a form accordion section.

  The badge reflects the current validation state of the section :

  1. errors   (red)    - validation errors rendered by Django
  2. missing  (yellow) - required fields left empty
  3. modified (green)  - values changed since page load

  this component must be placed on the <section class="fr-accordion"> element.
 */
Alpine.data('AccordionStatus', () => {
  return {
    errorCount: 0,
    missingCount: 0,
    modifiedCount: 0,
    initialValues: new Map(),

    init() {
      this.errorCount = this.$el.querySelectorAll('.fr-error-text').length;

      this.fields().forEach((element, index) => {
        this.initialValues.set(index, this.fieldValue(element));
      });
      this.refresh();

      this.$el.addEventListener('input', () => this.refresh());
      this.$el.addEventListener('change', () => this.refresh());

      // DSFR reads aria-expanded when it initializes the accordion (after Alpine),
      // so the section with errors is opened by the DSFR itself
      if (this.errorCount > 0) {
        this.$el
          .querySelector('.fr-accordion__btn')
          ?.setAttribute('aria-expanded', 'true');
      }
    },

    fields() {
      return Array.from(this.$el.querySelectorAll(FIELD_SELECTOR)).filter(
        (element) =>
          element.type !== 'hidden' && !element.disabled && element.name
      );
    },

    fieldValue(element) {
      if (element.type === 'checkbox' || element.type === 'radio') {
        return String(element.checked);
      }

      if (element.type === 'file') return String(element.files?.length ?? 0);
      return element.value;
    },

    isEmpty(element) {
      if (element.type === 'checkbox' || element.type === 'radio') {
        return !element.checked;
      }
      if (element.type === 'file') return !element.files?.length;
      return element.value.trim() === '';
    },

    refresh() {
      let missing = 0;
      let modified = 0;

      this.fields().forEach((element, index) => {
        if (element.required && this.isEmpty(element)) missing += 1;
        if (this.fieldValue(element) !== this.initialValues.get(index)) {
          modified += 1;
        }
      });

      this.missingCount = missing;
      this.modifiedCount = modified;
    },

    get badge() {
      if (this.errorCount > 0) {
        return {
          modifier: 'fr-badge--error',
          icon: 'fr-icon-error-fill',
          label: `${this.errorCount} ${isPlural('erreur', 'erreurs', this.errorCount)}`,
        };
      }

      if (this.missingCount > 0) {
        return {
          modifier: 'fr-badge--yellow-tournesol',
          icon: 'fr-icon-warning-fill',
          label: `${this.missingCount} ${isPlural(
            'information manquante',
            'informations manquantes',
            this.missingCount
          )}`,
        };
      }

      if (this.modifiedCount > 0) {
        return {
          modifier: 'fr-badge--success',
          icon: 'fr-icon-check-line',
          label: `${this.modifiedCount} ${isPlural(
            'modification à enregistrer',
            'modifications à enregistrer',
            this.modifiedCount
          )}`,
        };
      }

      return null;
    },
  };
});
