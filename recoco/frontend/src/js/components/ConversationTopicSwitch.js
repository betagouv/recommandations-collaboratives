import Alpine from 'alpinejs';
import { stringToColor } from '../utils/stringToColor';

Alpine.data('ConversationTopicSwitch', (projectId) => {
  return {
    topicSelector: 'general',
    historicSaveName: `conv-new-${projectId}`,
    valueTopicFormMessageSend: '',
    lastTopic: {
      slug: '',
      name: '',
    },
    stringToColor,
    init() {
      // Get the saved topic from local storage
      const { topicSlug: savedTopicSlug, topicName: savedTopicName } =
        JSON.parse(localStorage.getItem(this.historicSaveName)) || {
          savedTopicSlug: null,
          savedTopicName: null,
        };
      if (savedTopicSlug && savedTopicName) {
        // Select the saved topic
        this.setActiveTopic(savedTopicSlug, savedTopicName);
      } else {
        // Get the topic from the URL
        const params = new URLSearchParams(document.location.search);
        const topicSlug = params.get('topic-slug');
        const topicName = params.get('topic-name');

        if (topicSlug && topicName) {
          this.setActiveTopic(topicSlug, topicName);
        } else {
          const firstTopic = document.querySelector('[name="topic-selector"]');
          this.setActiveTopic(
            firstTopic.value,
            firstTopic.getAttribute('data-topic-name')
          );
          this.topicSelector = firstTopic.value;
        }
      }
      document.addEventListener('htmx:afterSwap', () => {
        this.showActiveTopicFeed();
        const inputMessage = document.querySelector('.tiptap.ProseMirror');
        if (!inputMessage) return;
        inputMessage.innerText = '';
      });
    },
    setActiveTopic(
      topicSlug = this.lastTopic.slug,
      topicName = this.lastTopic.name
    ) {
      this.topicSelector = topicSlug;
      this.showActiveTopicFeed(topicSlug, topicName);
    },
    showActiveTopicFeed(
      topicSlug = this.lastTopic.slug,
      topicName = this.lastTopic.name
    ) {
      localStorage.setItem(
        this.historicSaveName,
        JSON.stringify({ topicSlug, topicName })
      );
      window.history.pushState(
        {
          topicSlug: topicSlug,
          topicName: topicName,
        },
        '',
        `?topic-slug=${topicSlug}&topic-name=${topicName || 'Général'}`
      );
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
