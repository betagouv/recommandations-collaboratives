import Alpine from 'alpinejs';
import api, { hitcountUrl } from '../utils/api';

Alpine.data(
  'MarkDiagAsDone',
  (currentUserId, projectId, isDiagDone = false) => {
    return {
      displayDiagButton: isDiagDone,
      handleClickMarkDiagAsDone() {
        this.displayDiagButton = true;
        api.post(hitcountUrl(), {
          content_object_ct: 'auth.user',
          content_object_id: currentUserId,
          context_object_ct: 'projects.project',
          context_object_id: projectId,
        });
      },
    };
  }
);
