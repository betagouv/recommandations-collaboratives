import Alpine from 'alpinejs';
import api, { regionsUrl } from '../utils/api';

Alpine.data(
  'RegionDepartmentPreparer',
  ({ selectedDepartments = [] } = {}) => ({
    objectsToSelect: [],
    selectedDepartments,
    async init() {
      try {
        const regions = (await api.get(regionsUrl())).data;
        this.objectsToSelect = [...regions]; // Force new array reference for Alpine reactivity
      } catch (error) {
        throw new Error('Error fetching regions', error);
      }
    },
  })
);
