import Alpine from 'alpinejs';

/**
  Dismissible Notice Component

  Hides an information banner when the user closes it, and remembers that
  choice :

  - scope "local"   : kept for good (localStorage)
  - scope "session" : kept until the tab is closed (sessionStorage)

  Usage :
    <div x-data="DismissibleNotice('site-config.logos')" x-show="visible" x-cloak>
*/
Alpine.data('DismissibleNotice', (key, scope = 'local') => {
  return {
    visible: true,

    init() {
      this.visible = this.storage()?.getItem(key) !== 'true';
    },

    dismiss() {
      this.visible = false;
      try {
        this.storage()?.setItem(key, 'true');
      } catch {
      }
    },

    storage() {
      try {
        return scope === 'session'
          ? window.sessionStorage
          : window.localStorage;
      } catch {
        return null;
      }
    },
  };
});
