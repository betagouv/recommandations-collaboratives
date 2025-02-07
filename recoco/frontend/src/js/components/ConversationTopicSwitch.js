import Alpine from 'alpinejs';
import { stringToColor } from '../utils/utils';

Alpine.data('ConversationTopicSwitch', (topicList) => {
  return {
    topicList: topicList,
    topicSelector: 'general',
    valueTopicFormMessageSend: '',
    stringToColor,
    init() {
      this.setActiveTopic('general', '');
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
      this.$dispatch('topic-switched'); // trigger method scrollToFirstNotification
    },
  };
});
