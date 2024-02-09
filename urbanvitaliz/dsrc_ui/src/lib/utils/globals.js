import Alpine from 'alpinejs';

document.addEventListener('DOMContentLoaded', function () {
	if (window.Alpine === undefined) {
		window.Alpine = Alpine;

		Alpine.start();
	}
});

export default Alpine;
