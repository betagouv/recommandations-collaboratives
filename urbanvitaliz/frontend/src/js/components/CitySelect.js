import Alpine from 'alpinejs'

Alpine.data("CitySearch", CitySearch)

function CitySearch() {
    return {
        // other default properties
        isLoading: false,
        postal: null,
        cities: null,
        setPostcode(postcode) {
            this.postal = postcode
        },
        getPostcode(postcode, insee) {
            this.postal = postcode;
            this.fetchCities(insee)
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
