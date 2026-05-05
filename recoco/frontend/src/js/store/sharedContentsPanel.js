import Alpine from 'alpinejs';

const TAB_HASHES = {
  recommendations: 'actions',
  files: 'files',
  'draft-recommendations': 'drafts',
};

function replaceUrlHash(hash) {
  const url = hash
    ? `${window.location.pathname}${window.location.search}#${hash}`
    : `${window.location.pathname}${window.location.search}`;
  window.history.replaceState(null, '', url);
}

Alpine.store('sharedContentsPanel', {
  isOpen: false,
  activeTab: 'recommendations', // 'recommendations' | 'files' | 'draft-recommendations'
  lastActiveTab: 'recommendations', // 'recommendations' | 'files' | 'draft-recommendations'
  recommendations: [],
  files: [],
  draftRecommendations: [],
  externalFiles: [], // Files from EDL (État des lieux)
  privateFiles: [], // Files from private notes
  shouldReopenOnDetailClose: false, // Track if we should re-open when detail panel closes

  open(tab = null) {
    if (tab) {
      this.activeTab = tab;
      this.lastActiveTab = tab;
    }
    this.isOpen = true;

    // Prevent body scroll when panel is open
    document.body.style.overflow = 'hidden';

    replaceUrlHash(TAB_HASHES[this.activeTab]);
  },

  close() {
    this.isOpen = false;

    // Restore body scroll
    document.body.style.overflow = '';

    replaceUrlHash(null);
  },

  switchTab(tab) {
    this.activeTab = tab;
    this.lastActiveTab = tab;
    if (this.isOpen) {
      replaceUrlHash(TAB_HASHES[tab]);
    }
  },

  setRecommendations(recommendations) {
    this.recommendations = recommendations;
  },

  setFiles(files) {
    this.files = files;
  },

  setExternalFiles(externalFiles) {
    this.externalFiles = externalFiles;
  },

  setPrivateFiles(privateFiles) {
    this.privateFiles = privateFiles;
  },

  setDraftRecommendations(draftRecommendations) {
    this.draftRecommendations = draftRecommendations;
  },

  removeDraftRecommendation(recommendationId) {
    this.draftRecommendations = this.draftRecommendations.filter(
      (draft) => draft.id !== recommendationId
    );
  },

  /**
   * Close the panel but mark that we want to re-open it when the detail panel closes
   * Used when navigating from shared contents list to recommendation detail
   * Does not clear the URL hash since the detail panel will set its own (#action-{id}).
   */
  closeForDetail() {
    this.shouldReopenOnDetailClose = true;
    this.isOpen = false;
    document.body.style.overflow = '';
  },

  /**
   * Called when the resource detail panel closes and we should return to the list
   * Checks the flag and re-opens the panel if needed
   */
  reopenIfNeeded() {
    if (this.shouldReopenOnDetailClose) {
      this.shouldReopenOnDetailClose = false;
      this.open(this.lastActiveTab);
    }
  },

  /**
   * Get total count of recommendations
   */
  get recommendationsCount() {
    return this.recommendations.length;
  },

  /**
   * Get total count of files (conversation + external)
   */
  get filesCount() {
    return (
      this.files.length + this.externalFiles.length + this.privateFiles.length
    );
  },

  /**
   * Get total count of draft recommendations
   */
  get draftRecommendationsCount() {
    return this.draftRecommendations.length;
  },
  /**
   * Get total count of all shared contents
   */
  get totalCount() {
    return (
      this.recommendationsCount +
      this.draftRecommendationsCount +
      this.filesCount
    );
  },
});

export default Alpine.store('sharedContentsPanel');
