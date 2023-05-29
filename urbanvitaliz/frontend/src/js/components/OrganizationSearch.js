import Alpine from 'alpinejs'

function OrganizationSearch(currentOrganization) {
    return {
        organization:'',
        init() {
            console.log('OrganizationSearch ready', currentOrganization)
            this.organization = currentOrganization
        },
        handleOrganizationChange(e) {
            e.preventDefault();
            console.log('e value', e.target.value);
            console.log('e value length', e.target.value.length);
        }
    }
}

Alpine.data("OrganizationSearch", OrganizationSearch)
