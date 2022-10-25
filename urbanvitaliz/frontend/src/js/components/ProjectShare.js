import Alpine from 'alpinejs'

function ProjectShare() {
    return {
        initPublicShareModal() {
            const element = document.getElementById("public-share-modal");
            this.publicShareModal = new bootstrap.Modal(element);
        },
        openPublicShareModal() {
            this.publicShareModal.show();
        },
        initInviteMemberModal() {
            const element = document.getElementById("invite-member-modal");
            this.inviteMemberModal = new bootstrap.Modal(element);
        },
        openInviteMemberModal() {
            this.inviteMemberModal.show();
        },
        initInviteSwitchtenderModal() {
            const element = document.getElementById("invite-switchtender-modal");
            this.inviteSwitchtenderModal = new bootstrap.Modal(element);
        },
        openInviteSwitchtenderModal() {
            this.inviteSwitchtenderModal.show();
        },
    }
}

Alpine.data("ProjectShare", ProjectShare)


