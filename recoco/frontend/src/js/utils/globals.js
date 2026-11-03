import Alpine from 'alpinejs';
import focus from '@alpinejs/focus';
import Tooltip from '@ryangjchandler/alpine-tooltip';

document.addEventListener('DOMContentLoaded', function () {
  Alpine.plugin(focus);
  Alpine.plugin(Tooltip);
  if (!window.Alpine) (window.Alpine = Alpine).start();
});

export default Alpine;
