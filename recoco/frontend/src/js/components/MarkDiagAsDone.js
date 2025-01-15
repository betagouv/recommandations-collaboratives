import Alpine from 'alpinejs';
import api, { hitcountUrl, projectUrl } from '../utils/api';

Alpine.data(
  'MarkDiagAsDone',
  (currentUserId, projectId, isDiagDone = false) => {
    return {
      displayDiagButton: !isDiagDone,
      // async init() {
      //   const response = await api.get(projectUrl(projectId));
      //   console.log(response.data);
      //   console.log(response.data.is_diagnostic_done);
      //   response.status === 200 &&
      //     (this.displayDiagButton = !response.data.is_diagnostic_done);
      // },
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
