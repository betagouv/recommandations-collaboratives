import Alpine from 'alpinejs';
import { Modal } from 'bootstrap';

function ProjectShare() {
  return {
    initPublicShareModal() {
      const element = document.getElementById('public-share-modal');
      this.publicShareModal = new Modal(element);
    },
    openPublicShareModal() {
      this.publicShareModal.show();
    },
    initInviteMemberModal() {
      const element = document.getElementById('invite-member-modal');
      this.inviteMemberModal = new Modal(element);
    },
    openInviteMemberModal() {
      this.inviteMemberModal.show();
    },
    initInviteSwitchtenderModal() {
      const element = document.getElementById('invite-switchtender-modal');
      this.inviteSwitchtenderModal = new Modal(element);
    },
    openInviteSwitchtenderModal() {
      this.inviteSwitchtenderModal.show();
    },
  };
}

Alpine.data('ProjectShare', ProjectShare);
