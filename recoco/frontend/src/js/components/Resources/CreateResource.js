import Alpine from 'alpinejs';
import api from '../../utils/api';

Alpine.data('CreateResource', () => {
  return {
    is_draft: true,
    keywords_options: [],
    newRessourcePayload: {
      title: '',
      subtitle: '',
      summary: '',
      content: '',
      status: 'DRAFT',
      category: '',
      keywords: [],
      support_orga: '',
      departments: [],
      expires_on: '',
      contacts: [],
    },
    options: [
      {
        value: 'PRE_DRAFT',
        text: 'Incomplet',
      },
      {
        value: 'DRAFT',
        text: 'A modérer',
      },
      {
        value: 'TO_PROCESS',
        text: 'A traiter',
      },
      {
        value: 'VALIDATED',
        text: 'Validé',
      },
      {
        value: 'REJECTED',
        text: 'Refusé',
      },
    ],
    init() {
      console.log('CreateResource');
      this.fetchKeywords();
    },
    fetchKeywords() {
      // api.get('/keywords').then(response => {
      //   this.keywords_options = response.data;
      // });
      this.keywords_options = [
        {
          id: 1,
          text: 'Environnement',
          value: 'environnement',
          search: 'environnement',
        },
        { id: 2, text: 'Économie', value: 'economie', search: 'economie' },
        { id: 3, text: 'Social', value: 'social', search: 'social' },
      ];
    },
  };
});
