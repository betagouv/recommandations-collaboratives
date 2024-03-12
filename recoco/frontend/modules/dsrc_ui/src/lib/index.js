import 'vite/modulepreload-polyfill'; // needed by django_vite : https://github.com/MrBin99/django-vite/tree/multi-config?tab=readme-ov-file#assets

//  External dependencies
import '../ext/dsfr'; // DSFR (Système de Design de l'État) - JS

// Initialize AlpineJS
// import './utils/globals';

// Ajv
// import * as validations from '../ext/ajv.validations.default';

//Global Store
// import './lib/store/forms';

// import './styles/scss/core/index';
// Global reused components
import DsrcFormValidator from './components/forms/DsrcFormValidator'; // provides form validation for `dsrc_crispy_forms` that have an associated JSON schema
// export default { DsrcFormValidator, validations };
export default { DsrcFormValidator };

console.log('DSRC main added');
