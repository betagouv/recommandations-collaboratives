import Alpine from 'alpinejs';
// import { DsrcFormValidator } from 'dsrc_ui';

document.addEventListener('DOMContentLoaded', function () {
	window.Alpine = Alpine;
	// Alpine.plugin(DsrcFormValidator);
	Alpine.start();
});

export default Alpine;
