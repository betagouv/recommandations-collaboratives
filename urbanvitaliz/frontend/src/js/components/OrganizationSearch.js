import Alpine from 'alpinejs'
import api, { searchOrganizationsUrl } from '../utils/api'

function OrganizationSearch(currentOrganization) {
    return {
        organization: '',
        results: [],
        init() {
            console.log('OrganizationSearch ready', currentOrganization)
            this.organization = currentOrganization
        },
        async handleOrganizationChange(e) {
            e.preventDefault();

            try {
                if (e.target.value.length > 2) {
                    const results = await api.get(searchOrganizationsUrl(e.target.value))

                    if (results && results.data) {
                        return this.results = results.data
                    }
                } else {
                    return this.results = []
                }
            }
            catch (errors) {
                console.error('errors in organization search : ', errors)
            }
        },
        handleResultClick(result) {
            this.organization = result
        }
    }
}

Alpine.data("OrganizationSearch", OrganizationSearch)
