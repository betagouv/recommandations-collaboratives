import Alpine from 'alpinejs'

Alpine.data("CitySearch", CitySearch)

function CitySearch() {
    return {
        // other default properties
        isLoading: false,
        postal: null,
        cities: null,
    
        getPostcode(postcode, insee) {

            const postCodeString = JSON.parse(postcode.textContent)
            const inseeString = JSON.parse(insee.textContent)

            if (postCodeString) this.postal = postCodeString
            if (inseeString) this.fetchCities(inseeString)

        },
        fetchCities(currentInsee = null) {

            if (this.postal == "")
                return

            this.isLoading = true;
            fetch(`/api/communes/?postal=${this.postal}`)
                .then(res => res.json())
                .then(data => {
                    this.isLoading = false;
                    this.cities = data;
                }).finally(() => {
                    if (currentInsee) this.$refs.insee.value = currentInsee;
                });
        }
    }
}
