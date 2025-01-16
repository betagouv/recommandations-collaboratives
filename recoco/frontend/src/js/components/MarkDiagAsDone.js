import Alpine from 'alpinejs';
import api, { projectUrl } from '../utils/api';

Alpine.data(
  'MarkDiagAsDone',
  (currentUserId, projectId, isDiagDone = false) => {
    return {
      displayDiagButton: !isDiagDone,
      async handleClickMarkDiagAsDone() {
        const response = await api.patch(projectUrl(projectId), {
          is_diagnostic_done: true,
        });
        if (response.status !== 200) {
          throw new Error('Error while marking the diag as done');
        }
        this.displayDiagButton = false;
      },
    };
  }
);
