import Alpine from 'alpinejs';
import api from '../../utils/api';

Alpine.data('CreateResource', () => {
  return {
    init() {
      console.log('CreateResource');
    },
  };
});
