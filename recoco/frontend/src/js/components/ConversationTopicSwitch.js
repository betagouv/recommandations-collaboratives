import Alpine from 'alpinejs';
import { stringToColor } from '../utils/utils';

Alpine.data('ConversationTopicSwitch', (topicList) => {
  return {
    topicList: topicList,
    topicSelector: 'general',
    stringToColor,
    setActiveTopic(event) {
      Array.from(document.querySelectorAll('.feed-element-item')).forEach(
        (element) => {
          if (
            (event.target.value === 'general' &&
              element.getAttribute('data-topic') === '') ||
            element.getAttribute('data-topic') === event.target.value
          ) {
            element.classList.remove('d-none');
            return;
          }
          element.classList.add('d-none');
        }
      );
    },
  };
});
