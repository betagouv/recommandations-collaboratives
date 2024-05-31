import Alpine from 'alpinejs';

Alpine.data('DsrcSelect', DsrcSelect);

function DsrcSelect() {
	return {
		// other default properties
		isLoading: false,
		options: null,
		fetchOptions(url) {
			this.isLoading = true;
			fetch(url)
				.then((res) => res.json())
				.then((data) => {
					this.options = data;
				})
				.catch((e) => {
					// Handle error
				})
				.finally(() => {
					this.isLoading = false;
				});
		},
	};
}
