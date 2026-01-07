import Alpine from 'alpinejs';
import api from '../../utils/api';

Alpine.data('CreateResource', () => {
  return {
    is_draft: true,
    keywords_options: [],
    init() {
      console.log('CreateResource');
      this.fetchKeywords();
    },
    fetchKeywords() {
      // api.get('/keywords').then(response => {
      //   this.keywords_options = response.data;
      // });
      this.keywords_options = [
        { id: 1, text: 'Environnement', value: 'environnement', search: 'environnement' },
        { id: 2, text: 'Économie', value: 'economie', search: 'economie' },
        { id: 3, text: 'Social', value: 'social', search: 'social' },
      ];
    },
  };
});
