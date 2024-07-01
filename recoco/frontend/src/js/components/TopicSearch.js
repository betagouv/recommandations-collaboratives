import Alpine from 'alpinejs';
import api, { searchTopicsUrl } from '../utils/api';

function TopicSearch(currentTopic, restrict_to = null) {
  return {
    topic: '',
    results: [],
    restrict_to: null,
    deleted: false,
    async init() {
      this.topic = currentTopic;
      this.restrict_to = restrict_to;
      if (currentTopic) {
        const json = await api.get(
          searchTopicsUrl(currentTopic, this.restrict_to)
        );
        if (json.data.count > 0) {
          return (this.results = results.data.results);
        }
      }
    },
    async handleTopicChange(e) {
      e.preventDefault();

      try {
        if (e.target.value.length > 2) {
          const json = await api.get(
            searchTopicsUrl(e.target.value, this.restrict_to)
          );

          if (json.data.count > 0) {
            return (this.results = results.data.results);
          }
        } else {
          return (this.results = []);
        }
      } catch (errors) {
        console.error('errors in topic search : ', errors);
      }
    },
    handleResultClick(result) {
      this.topic = result;
    },

    handleDeleteClick() {
      this.deleted = !this.deleted;
    },
  };
}

Alpine.data('TopicSearch', TopicSearch);
