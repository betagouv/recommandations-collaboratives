import Alpine from 'alpinejs';
import api from '../../utils/api';

Alpine.data('CreateResource', () => {
  return {
    is_draft: true,
    init() {
      console.log('CreateResource');
    },
  };
});
