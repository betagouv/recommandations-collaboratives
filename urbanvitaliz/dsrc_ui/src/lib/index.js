import 'vite/modulepreload-polyfill'; // needed by django_vite : https://github.com/MrBin99/django-vite/tree/multi-config?tab=readme-ov-file#assets

//  External dependencies
import '../ext/dsfr'; // DSFR (Système de Design de l'État) - JS

// Initialize AlpineJS
import './utils/globals';

//Global Store
// import './lib/store/forms';

// Global reused components
import './components/forms/DsrcFormValidator'; // provides form validation for `dsrc_crispy_forms` that have an associated JSON schema

console.log('js main added');
