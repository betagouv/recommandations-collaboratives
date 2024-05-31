import { Dropdown } from 'bootstrap';
import Alpine from 'alpinejs';
import api, {
  markAllNotificationsAsReadUrl,
  notificationsMarkAsReadByIdUrl,
} from '../utils/api';
import appStore from '../store/app';
import { ToastType } from '../models/toastType';

function MenuNotifications(notificationNumber) {
  console.log('notificationNumber', notificationNumber);
  return {
    notificationNumber: notificationNumber,
    async markNotificationAsRead(notificationId, el) {
      try {
        const reqMarkNotifAsRead = await api.patch(
          notificationsMarkAsReadByIdUrl(notificationId),
          {}
        );
        if (reqMarkNotifAsRead.data.marked_as_read > 0) {
          this.removeNotificationInDom(el);
        }
      } catch (error) {
        this.showToast(
          'Erreur lors de la mise à jour de la notification. Merci de réessayer plus tard.'
        );
        return;
      }
    },
    async markAllNotificationsAsRead() {
      try {
        await api.patch(markAllNotificationsAsReadUrl(), {});
        this.notificationNumber = 0;
      } catch (error) {
        this.showToast(
          'Erreur lors de la mise à jour des notifications. Merci de réessayer plus tard.'
        );
        return;
      }
    },
    removeNotificationInDom(el) {
      this.notificationNumber -= 1;
      el.parentElement.remove();
    },
    closeNotificationsMenu() {
      const notificationsMenu = document.querySelector(
        '.dropdown-menu.notifications'
      );
      const dropdownInstance = new Dropdown(notificationsMenu);
      dropdownInstance.hide();
    },
    showToast(message, type) {
      appStore.notification.message = message;
      appStore.notification.timeout = 5000;
      appStore.notification.isOpen = true;
      appStore.notification.type = type || ToastType.error;
    },
  };
}

Alpine.data('MenuNotifications', MenuNotifications);
