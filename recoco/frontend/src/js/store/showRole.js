import Alpine from 'alpinejs';
// import { document } from 'postcss';

/**
 * Alpine.js store for managing the showRole state.
 *
 * @store showRole
 *
 * @method init - Show the role if the showRole store exist (and is true).
 * @method setShowToTrue - Sets the showRole store to true.
 */

Alpine.store('showRole', {
  init() {
    const showRole = localStorage.getItem('showRole');
    if (showRole) {
      //   alert("on devrait voir la modal s'ouvir");
      document.getElementById('select-observer-or-advisor-button').click();
      localStorage.removeItem('showRole');
    } else {
      //   alert("on devrait pas voir la modal s'ouvrir");
    }
  },

  setShowToTrue() {
    localStorage.setItem('showRole', true);
  },
});

export default Alpine.store('showRole');
