//Bootstrap librairie
// import 'bootstrap/dist/css/bootstrap.min.css';
import '../css/custom-bootstrap.scss';
import '@gouvfr/dsfr/dist/dsfr.min.css';
import '@gouvfr/dsfr/dist/utility/utility.min.css';
import '@gouvfr/dsfr/dist/dsfr.module.min';

// Specific styles
import '../css/specificStyle.scss';

// DSFR custom
import '../css/DSFR/custom-dsfr.scss';
import '../css/DSFR/marianne.css';
// Tooltips
import 'tippy.js/dist/tippy.css';

import 'vite/modulepreload-polyfill';
import './utils/globals';
import './utils/tooltipInitialization.js';

//Global Store
import './store/utils';
import './store/editor';
import './store/djangoData';
import './store/app';
import './store/crisp';

//Global reused component
import './components/Notification';
import './components/Editor';
import './components/FieldValidator';
import './components/Toast';
import './components/Crisp';

//Global CSS
import '../css/buttons.css';
import '../css/input.css';
import '../css/typography.css';
import '../css/hover.css';
import '../css/colors.css';
import '../css/text-colors.css';
import '../css/border.css';
import '../css/role.css';
import '../css/custom-icon.css';

//Layouts CSS
import '../css/layouts/stack.css';

//Global reused component CSS
import '../css/flags.css';
import '../css/userCard.scss';
import '../css/callout.css';
import '../css/markdown.css';
import '../css/miscellaneous.css';

/**
 * MATOMO TRACKING
 */

import {
  trackClickOnRecoLink,
  trackClickOnFileLink,
  trackScrollDepth,
  trackReplyToMessage,
  trackOpenRessource,
  trackSeeMoreParticipants,
  trackCopyContactEmail,
} from './utils/trackingMatomo';

window.trackCopyContactEmail = trackCopyContactEmail;
window.trackClickOnRecoLink = trackClickOnRecoLink;
window.trackClickOnFileLink = trackClickOnFileLink;
window.trackScrollDepth = trackScrollDepth;
window.trackReplyToMessage = trackReplyToMessage;
window.trackOpenRessource = trackOpenRessource;
window.trackSeeMoreParticipants = trackSeeMoreParticipants;
