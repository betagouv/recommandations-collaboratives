import Alpine from 'alpinejs';
import api, { hitcountUrl } from '../utils/api';

Alpine.data(
  'ClickToSeeUser',
  (ownerId, currentUserId, currentUserIsStaff, projetId, userToDiplay = []) => {
    return {
      userId: ownerId,
      displayUser: false,
      init() {
        if (
          currentUserIsStaff ||
          ownerId === currentUserId ||
          userToDiplay.includes(ownerId)
        ) {
          this.displayUser = true;
          return;
        }
      },
      handleClickToSeeInfo() {
        api.post(hitcountUrl(), {
          content_object_ct: 'auth.user',
          content_object_id: this.userId,
          context_object_ct: 'projects.project',
          context_object_id: projetId,
        });

        this.displayUser = true;
      },
    };
  }
);
