import { Dropdown } from 'bootstrap';
import Alpine from 'alpinejs';
import api, {
  djangoNotificationsMarkAsReadBySlugUrl,
  djangoNotificationsUnreadListUrl,
  markAllNotificationsAsReadUrl,
} from '../utils/api';

function MenuNotifications(notificationNumber) {
  console.log('notificationNumber', notificationNumber);
  return {
    notificationNumber: notificationNumber,
    async markNotificationAsRead(notificationId, el) {
      const reqListNotif = await api.get(
        djangoNotificationsUnreadListUrl(),
        {}
      );
      if (reqListNotif.status != 200) {
        return;
      }

      const notificationToRead = reqListNotif.data.unread_list.find(
        (n) => n.id === notificationId
      );
      if (!notificationToRead) {
        return;
      }

      const reqMarkNotifAsRead = await api.get(
        djangoNotificationsMarkAsReadBySlugUrl(notificationToRead.slug),
        {}
      );
      if (reqMarkNotifAsRead.status != 200) {
        return;
      }

      this.removeNotificationInDom(el);
    },
    async markAllNotificationsAsRead() {
      const resp = await api.post(markAllNotificationsAsReadUrl(), {});
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
