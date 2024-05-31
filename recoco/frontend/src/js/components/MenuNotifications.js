import { Dropdown } from 'bootstrap';
import Alpine from 'alpinejs';
import api, {
  markAllNotificationsAsReadUrl,
  notificationsMarkAsReadByIdUrl,
} from '../utils/api';

function MenuNotifications(notificationNumber) {
  console.log('notificationNumber', notificationNumber);
  return {
    notificationNumber: notificationNumber,
    async markNotificationAsRead(notificationId, el) {
      const reqMarkNotifAsRead = await api.patch(
        notificationsMarkAsReadByIdUrl(notificationId),
        {}
      );
      if (reqMarkNotifAsRead.status != 200) {
        return;
      }
      if (reqMarkNotifAsRead.data.marked_as_read > 0) {
        this.removeNotificationInDom(el);
      }
    },
    async markAllNotificationsAsRead() {
      const resp = await api.patch(markAllNotificationsAsReadUrl(), {});
      if (resp.status === 200) {
        this.notificationNumber = 0;
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
  };
}

Alpine.data('MenuNotifications', MenuNotifications);
