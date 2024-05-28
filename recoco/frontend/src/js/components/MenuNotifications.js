import Alpine from 'alpinejs';
import api, {
  markAllNotificationsAsReadUrl,
  markTaskNotificationsAsReadUrl,
} from '../utils/api';

function MenuNotifications(notificationNumber) {
  console.log('notificationNumber', notificationNumber);
  return {
    notificationNumber: notificationNumber,
    init(notificationNumber) {
      console.log('notificationNumber', notificationNumber);
    },
    async markNotificationAsRead(projectId, taskId, el) {
      const resp = await api.post(
        markTaskNotificationsAsReadUrl(projectId, taskId),
        {}
      );
      if (resp.status === 200) {
        // delete notification in DOM
        this.notificationNumber -= 1;
        el.parentElement.remove();
      }
    },
    async markAllNotificationsAsRead() {
      // console.log('markAllNotificationsAsRead');
      const resp = await api.post(markAllNotificationsAsReadUrl(), {});
      if (resp.status === 200) {
        // delete all notifications in DOM
      }
    },
  };
}

Alpine.data('MenuNotifications', MenuNotifications);
