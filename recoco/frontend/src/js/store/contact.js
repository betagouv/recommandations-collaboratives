import Alpine from '../utils/globals';

document.addEventListener('alpine:init', () => {
  Alpine.store('contact', {
    orgaSelected : null,
    // setOrgaSelected(orga) {
    //   this.orgaSelected = orga;
    // },
  });
});
