import Alpine from '../../utils/globals';

Alpine.data('TaskCardPanel', (reco) => ({
  recommendation: null,
  element: null,
  async openResourcePreviewPanel(recommendation, element) {
    // Close the shared contents panel but mark for re-open when returning
    Alpine.store('sharedContentsPanel').closeForDetail();

    // Open the resource preview panel
    if (Alpine.store('resourcePreviewPanel')) {
      Alpine.store('resourcePreviewPanel').open(recommendation, element);
    }
  },
  syncTask() {
    // Fusion makes the recommendation object truely reactive
    this.recommendation = {
      ...Alpine.store('sharedContentsPanel').recommendations.find(r => r.id === reco.id) || Alpine.store('sharedContentsPanel').draftRecommendations.find(r => r.id === reco.id) || reco,
      ...Alpine.store('tasksData').getTaskById(reco.id)
    };

    this.element = { id: this.recommendation.messageId, posted_by: this.recommendation.messagePostedBy };
  }
}));
