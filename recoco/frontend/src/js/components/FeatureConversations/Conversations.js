import Alpine from '../../utils/globals';
import api, {
  conversationsMessagesUrl,
  contactUrl,
  conversationsParticipantsUrl,
  documentUrl,
} from '../../utils/api';

Alpine.data('Conversations', (projectId) => ({
  projectId,
  feed: {},
  messages: [],
  tasks: [],
  users: [],
  messagesParticipants: [],
  documents: [],
  init() {
    this.getMessages();
    this.getMessagesParticipants();
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
  async getMessagesParticipants() {
    try {
      const messagesParticipants = await api.get(
        conversationsParticipantsUrl(this.projectId)
      );
      this.messagesParticipants = messagesParticipants.data;
    } catch (error) {
      throw new Error('Failed to get messages participants');
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
  getUserById(id) {
    const foundUser = this.messagesParticipants.find((user) => user.id === +id);
    if (!foundUser) {
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
      return user.data;
    }
    return foundUser;
  },
  async getDocumentById(id) {
    const foundDocument = this.documents.find(
      (document) => document.id === +id
    );
    if (!foundDocument) {
      const document = await api.get(documentUrl(this.projectId, id));
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
