import Alpine from '../utils/globals';

document.addEventListener('alpine:init', () => {
  Alpine.store('contact', {
    orgaSelected: null,
    groupSelected: null,
    createdContact: null,
    createdOrganisation: null,
  });
});
