import Alpine from '../utils/globals';

document.addEventListener('alpine:init', () => {
  Alpine.store('contact', {
    orgaSelected: null,
    orgaCreated: null,
    groupSelected: null,
    createdContact: null,
    selectedDepartments: [],
  });
});
