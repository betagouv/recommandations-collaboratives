import '../components/FeatureAddContact/SearchContactModal.js';
import '../components/FeatureAddContact/CreateContactModal.js';
import '../components/SearchOrganisation.js';
import getContact from '../utils/getContact';
import { formatDate } from '../utils/date';

// Make getContact available globally for Alpine.js components
window.getContact = getContact;
window.formatDate = formatDate;
