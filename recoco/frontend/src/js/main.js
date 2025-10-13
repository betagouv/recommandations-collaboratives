//Bootstrap librairie
// import 'bootstrap/dist/css/bootstrap.min.css';
import '../css/main.scss';
import '@gouvfr/dsfr/dist/dsfr.min.css';
import '@gouvfr/dsfr/dist/utility/utility.min.css';
import '@gouvfr/dsfr/dist/dsfr.module.min';

import 'vite/modulepreload-polyfill';
import './utils/globals';
import './utils/tooltipInitialization.js';

//Global Store
import './store/utils';
import './store/editor';
import './store/djangoData';
import './store/app';

//Global reused component
import './components/Notification';
import './components/Editor';
import './components/FieldValidator';
import './components/Toast';

//Global CSS
import '../css/dsfr-custom.css';
import '../css/buttons.css';
import '../css/input.css';
import '../css/typography.css';
import '../css/hover.css';
import '../css/colors.css';
import '../css/text-colors.css';
import '../css/border.css';
import '../css/role.css';
import '../css/custom-icon.css';
import '../css/main.css';

//Layouts CSS
import '../css/layouts/stack.css';

//Global reused component CSS
import '../css/flags.css';
import '../css/userCard.scss';
import '../css/callout.css';
import '../css/markdown.css';
import '../css/miscellaneous.css';
