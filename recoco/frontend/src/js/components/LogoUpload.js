import Alpine from 'alpinejs';

/**
  Logo Upload Component

  Manages the state of a logo upload field,
  allowing users to remove or replace the logo.
*/
Alpine.data('LogoUpload', () => {
  return {
    removed: false,
    replaced: false,

    remove() {
      this.removed = true;
      this.replaced = false;
    },

    onSelect(event) {
      this.replaced = event.target.files.length > 0;
      if (this.replaced) this.removed = false;
    },
  };
});
