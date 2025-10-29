import Alpine from 'alpinejs';

Alpine.data('NewFeatureBanner', ({ codeFeature, maxViewed } = {}) => ({
  shouldShow: false,
  codeFeature: codeFeature || 'conversations',
  maxViewed: maxViewed || 4,
  newFeatureBanner: {
    conversations: {
      bannerViewed: 0,
    },
  },
  init() {
    let newFeatureBanner = JSON.parse(localStorage.getItem('newFeatureBanner'));
    if (!newFeatureBanner) {
      newFeatureBanner = { ...this.newFeatureBanner };
    }

    if (newFeatureBanner[this.codeFeature].bannerViewed >= this.maxViewed) {
      return;
    }
    newFeatureBanner[this.codeFeature].bannerViewed += 1;
    this.shouldShow = true;
    localStorage.setItem('newFeatureBanner', JSON.stringify(newFeatureBanner));
  },
  hide() {
    this.shouldShow = false;
    this.newFeatureBanner[this.codeFeature].bannerViewed = this.maxViewed;
    localStorage.setItem(
      'newFeatureBanner',
      JSON.stringify(this.newFeatureBanner)
    );
  },
}));
