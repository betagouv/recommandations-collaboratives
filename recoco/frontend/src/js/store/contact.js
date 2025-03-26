import Alpine from '../utils/globals';

document.addEventListener('alpine:init', () => {
  Alpine.store('contact', {
    orgaSelected: null,
    createdContact: null,
    openModal: '',
  });
});
