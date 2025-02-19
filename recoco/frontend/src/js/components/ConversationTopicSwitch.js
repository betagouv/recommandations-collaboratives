import Alpine from 'alpinejs';
import { stringToColor } from '../utils/utils';

Alpine.data('ConversationTopicSwitch', (currentTopic = 'general') => {
  return {
    topicSelector: currentTopic,
    valueTopicFormMessageSend: '',
    lastTopic: {
      slug: '',
      name: '',
    },
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
      document.addEventListener('htmx:load', () => {
        console.log('htmx:load');
      });
      document.addEventListener('htmx:afterSwap', () => {
        console.log('htmx:afterSwap');
        this.setActiveTopic();
        const inputMessage = document.querySelector('.tiptap.ProseMirror');
        if (!inputMessage) return;
        inputMessage.innerText = '';
      });
    },
    setActiveTopic(
      topicSlug = this.lastTopic.slug,
      topicName = this.lastTopic.name
    ) {
      window.history.pushState(
        {
          topicSlug: topicSlug,
          topicName: topicName,
        },
        '',
        `?topic-slug=${topicSlug}&topic-name=${topicName || 'Général'}`
      );
      // window.location = `?topic-slug=${topicSlug}&topic-name=${topicName}`;
      // window.location.replace(`https://example.com/#${location.pathname}`);
      debugger;
      this.lastTopic = {
        slug: topicSlug,
        name: topicName,
      };
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
      this.valueTopicFormMessageSend = topicName == 'Général' ? '' : topicName;
      this.$dispatch('topic-switched', topicSlug); // trigger method scrollToFirstNotification
    },
  };
});
