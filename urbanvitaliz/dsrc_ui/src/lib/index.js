import 'vite/modulepreload-polyfill'; // needed by django_vite : https://github.com/MrBin99/django-vite/tree/multi-config?tab=readme-ov-file#assets

// Initialize AlpineJS
import './utils/globals';

//Global Store
// import './lib/store/forms';

// Global reused component
import './components/forms/DsrcForm';

console.log('js main added');
