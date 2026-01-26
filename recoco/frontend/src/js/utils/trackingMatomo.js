const generateTrackEvent = (
  event,
  action,
  name,
  path = window.location.pathname
) => {
  if (window._paq === undefined) return;
  window._paq.push(['trackEvent', event, action, name, path]);
};
export const trackClickOnRecoLink = () => {
  generateTrackEvent('Click', 'reco-shortcut-link');
};

export const trackClickOnFileLink = () => {
  generateTrackEvent('Click', 'files-shortcut-link');
};

export const trackReplyToMessage = () => {
  generateTrackEvent('Click', 'reply-to-message');
};

export const trackOpenRessource = () => {
  generateTrackEvent('Click', 'open-ressource');
};

export const trackSeeMoreParticipants = () => {
  generateTrackEvent('Click', 'see-more-participants');
};

export const trackCopyContactEmail = () => {
  generateTrackEvent('Click', 'copy-contact-email');
};

export const trackScrollDepth = ({ pageLoaded }) => {
  if (!pageLoaded) {
    return;
  }
  let scrollDepth = Math.round(
    (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100
  );
  if (scrollDepth >= 25 && !window.scroll25) {
    generateTrackEvent('Scroll', '25%');
    window.scroll25 = true;
  }
  if (scrollDepth >= 50 && !window.scroll50) {
    generateTrackEvent('Scroll', '50%');
    window.scroll50 = true;
  }
  if (scrollDepth >= 75 && !window.scroll75) {
    generateTrackEvent('Scroll', '75%');
    window.scroll75 = true;
  }
};

export default {
  trackClickOnRecoLink,
  trackClickOnFileLink,
  trackScrollDepth,
  trackReplyToMessage,
  trackOpenRessource,
  trackSeeMoreParticipants,
  trackCopyContactEmail,
};
