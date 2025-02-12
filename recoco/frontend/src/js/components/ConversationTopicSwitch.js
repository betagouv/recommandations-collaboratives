import Alpine from 'alpinejs';
import { stringToColor } from '../utils/utils';

Alpine.data('ConversationTopicSwitch', (currentTopic = 'general') => {
  return {
    topicSelector: currentTopic,
    valueTopicFormMessageSend: '',
    stringToColor,
    init() {
      const params = new URLSearchParams(document.location.search);
      const topicSlug = params.get('topic-slug');
      const topicName = params.get('topic-name');

      if (topicSlug && topicName) {
        this.topicSelector = topicSlug;
        this.setActiveTopic(topicSlug, topicName);
        return;
      }
      const firstTopic = document.querySelector('[name="topic-selector"]');
      this.setActiveTopic(
        firstTopic.value,
        firstTopic.getAttribute('data-topic-name')
      );
      this.topicSelector = firstTopic.value;
    },
    setActiveTopic(topicSlug, topicName) {
      Array.from(
        document.querySelectorAll('[data-type-element="feed-element-item"]')
      ).forEach((element) => {
        if (
          (topicSlug === 'general' &&
            element.getAttribute('data-topic') === '') ||
          element.getAttribute('data-topic') === topicSlug
        ) {
          element.classList.remove('d-none');
          return;
        }
        element.classList.add('d-none');
      });
      this.valueTopicFormMessageSend = topicName;
      this.$dispatch('topic-switched', topicSlug); // trigger method scrollToFirstNotification
    },
  };
});
