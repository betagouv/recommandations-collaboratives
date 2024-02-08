import Alpine from "alpinejs";

Alpine.data("Crm", Crm)
Alpine.data("Note", Note)

function Crm() {
    return {
        init() {
            // Sidebar behaviour
            const sidebar = this.$refs.sidebar;
            const sidebarHeight = sidebar.offsetHeight;
            const windowHeight = window.innerHeight;

            if (sidebarHeight > windowHeight) {
                sidebar.classList.remove('crm-sticky')
                sidebar.classList.add('crm-relative')
            }

        },
        goBack() {
            console.debug('go back');
            window.history.back();
        }
    };
};

function Note() {
    return {
        isOpen: false,
        init() {
            const note = this.$refs.note;
            const noteToggleButton = this.$refs.noteToggleButton

            if (note && note.offsetHeight < 200) {
                note.classList.add('is-small')

                if (noteToggleButton) noteToggleButton.classList.add('hidden');
            }
        },
    };
};
