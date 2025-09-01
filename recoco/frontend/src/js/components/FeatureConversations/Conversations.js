import Alpine from '../../utils/globals';

Alpine.data('Conversations', (feed) => ({
  feed,
  getMessageById(id) {
    return this.feed.messages.find((message) => message.id === +id);
  },
  getShortMessageInReplyTo(id) {
    const shortMessage = this.getMessageById(id)
      .nodes.find((node) => node.type === 'markdown')
      .data.text.slice(0, 40);
    return shortMessage;
  },
}));
