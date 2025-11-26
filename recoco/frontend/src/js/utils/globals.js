import Alpine from 'alpinejs';
import focus from '@alpinejs/focus';

document.addEventListener('DOMContentLoaded', function () {
  Alpine.plugin(focus);
  if (!window.Alpine) (window.Alpine = Alpine).start();
});

export default Alpine;
