import Alpine from 'alpinejs';

function MenuNotifications() {
  return {
    init() {
      console.log('MenuNotifications initialized');
      // this.$store.notifications.init();
      // Get notifications
      console.log(this.notifications);
    },
    get notifications() {
      return this.$store.notifications.notifications;
    },
  };
}

Alpine.data('MenuNotifications', MenuNotifications);
