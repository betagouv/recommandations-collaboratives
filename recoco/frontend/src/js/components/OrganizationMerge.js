import Alpine from 'alpinejs';

Alpine.data('OrganizationMerge', OrganizationMerge);

function OrganizationMerge({ initialName = '' } = {}) {
  return {
    name: initialName,
    selectOrganization(event) {
      const tag = event.target.closest('button[data-org-name]');
      if (!tag) return;
      this.name = tag.dataset.orgName;
      event.stopPropagation();
    },
  };
}
