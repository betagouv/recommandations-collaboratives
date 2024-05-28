import Alpine from 'alpinejs';
import api, {
  djangoNotificationsMarkAsReadBySlugUrl,
  djangoNotificationsUnreadListUrl,
  markAllNotificationsAsReadUrl,
  markTaskNotificationsAsReadUrl,
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
      console.log('notificationToRead', notificationToRead);
      if (!notificationToRead) {
        return;
      }

      const reqMarkNotifAsRead = await api.get(
        djangoNotificationsMarkAsReadBySlugUrl(notificationToRead.slug),
        {}
      );
      console.log('resp2', reqMarkNotifAsRead);
      if (reqMarkNotifAsRead.status != 200) {
        return;
      }

      this.removeNotificationInDom(el);
    },
    async markAllNotificationsAsRead() {
      // console.log('markAllNotificationsAsRead');
      const resp = await api.post(markAllNotificationsAsReadUrl(), {});
      if (resp.status === 200) {
        // delete all notifications in DOM
      }
    },
    removeNotificationInDom(el) {
      this.notificationNumber -= 1;
      el.parentElement.remove();
    },
  };
}

Alpine.data('MenuNotifications', MenuNotifications);
