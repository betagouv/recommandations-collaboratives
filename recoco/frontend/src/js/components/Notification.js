import Alpine from 'alpinejs';
import appStore from '../store/app';
import '../../css/notification.css';

function Notification() {
  return {
    get isOpen() {
      if (
        this.$store.app.notification.isOpen &&
        this.$store.app.notification.message.length > 0
      ) {
        setTimeout(() => {
          appStore.notification.isOpen = false;
          appStore.notification.message = '';
        }, appStore.notification.timeout);
      }

      return this.$store.app.notification.isOpen;
    },
    get message() {
      return this.$store.app.notification.message;
    },
    get type() {
      return this.$store.app.notification.type;
    },
  };
}

Alpine.data('Notification', Notification);
