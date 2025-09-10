import Alpine from '../../utils/globals';
import api, { userUrl } from '../../utils/api';

Alpine.data('Conversations', (feed, projectId) => ({
  projectId,
  feed,
  users: [],
  documents: [],
  init() {},
  get recommendations() {
    return this.$store.tasksData.tasks;
  },
  getRecommendationById(id) {
    return this.recommendations.find((task) => task.id === id);
  },
  getMessageById(id) {
    return this.feed.messages.find((message) => message.id === +id);
  },
  getShortMessageInReplyTo(id) {
    const shortMessage = this.getMessageById(id)
      .nodes.find((node) => node.type === 'markdown')
      .data.text.slice(0, 40);
    return shortMessage;
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
}));
