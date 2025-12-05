import '../components/FeatureAddContact/SearchContactModal.js';
import '../components/FeatureAddContact/CreateContactModal.js';
import '../components/FeatureAddContact/CreateOrganizationModal.js';
import '../components/SearchOrganization.js';
import '../components/MultiSelectRegionDepartment.js';
import '../components/User';
import getContact from '../utils/getContact';
import { formatDate } from '../utils/date';

// Make getContact available globally for Alpine.js components
window.getContact = getContact;
window.formatDate = formatDate;
