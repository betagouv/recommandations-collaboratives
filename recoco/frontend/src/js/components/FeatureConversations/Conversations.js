import Alpine from '../../utils/globals';
import api, {
  userUrl,
  conversationsMessagesUrl,
  contactUrl,
} from '../../utils/api';

Alpine.data('Conversations', (projectId) => ({
  projectId,
  feed: {},
  messages: [],
  tasks: [],
  users: [],
  documents: [],
  init() {
    this.getMessages();
    this.$store.tasksData._subscribe(() => {
      this.tasks = this.$store.tasksData.tasks;
    });
  },
  getRecommendationById(id) {
    const foundRecommendation = this.tasks.find(
      (recommendation) => recommendation.id == id
    );
    return foundRecommendation;
  },
  getMessageById(id) {
    return this.feed.messages.find((message) => message.id === +id);
  },
  async getMessages() {
    try {
      const messages = await api.get(conversationsMessagesUrl(this.projectId));
      this.feed.messages = messages.data;
    } catch (error) {
      throw new Error('Failed to get messages');
    }
  },
  getShortMessageInReplyTo(id) {
    const shortMessage = this.getMessageById(id);
    if (!shortMessage) {
      return '';
    }
    const markdownNode = shortMessage.nodes.find(
      (node) => node.type === 'MarkdownNode'
    );
    return `${markdownNode.text.slice(0, 40)}${markdownNode.text.length > 40 ? '...' : ''}`;
  },
  async getUserById(id) {
    const foundUser = this.users.find((user) => user.id === +id);
    if (!foundUser) {
      // const user = await api.get(userUrl(id));
      /** MOCK DATA */
      const user = {};
      user.data = {
        id: +id,
        place: this.users.length,
        first_name: 'John',
        last_name: 'Doe',
        email: 'john.doe@example.com',
        phone_no: '0642424242',
        last_login: {
          date: '2021-01-01',
        },
        is_active: true,
        profile: {
          organization_position: 'Developer',
          organization: {
            name: 'Example Inc.',
          },
        },
      };
      this.users.push(user.data);
      return user.data;
    }
    return foundUser;
  },
  async getDocumentById(id) {
    // TODO: get document from API projects/${projectId}/documents/${id}/
    const foundDocument = this.documents.find(
      (document) => document.id === +id
    );
    if (!foundDocument) {
      // const user = await api.get(userUrl(id));
      /** MOCK DATA */
      const document = {};
      document.data = {
        id: +id,
        filename: 'Document.pdf',
        description: 'Description du document',
        title: 'Titre du document',
        size: '100KB',
        the_link: '/media/projects/198/wushu.png',
        uploaded_by: 1,
      };
      this.documents.push(document.data);
      return document.data;
    }
    return foundDocument;
  },
  async getContactById(id) {
    const contact = await api.get(contactUrl(id));
    return contact.data;
  },
}));
