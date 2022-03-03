function action_pusher_app() {
		return {
        isBusy: true,
        search: '',
        resources: [],

        push_type: 'single',
        intent: '',
        content: '',
        selected_resource: null,
        selected_resources: [],
        draft: false,

        get filteredResources() {
            if (this.search == '')
                return this.resources;

            return this.resources.filter(
                i => i.title.toLowerCase().includes(this.search.toLowerCase())
            ) || [];
        },

        truncate(input, size=30) {
            return input.length > size ? `${input.substring(0, size)}...` : input;
        },

        formatDateDisplay(date) {
                if (this.dateDisplay === 'toDateString') return new Date(date).toDateString();
                if (this.dateDisplay === 'toLocaleDateString') return new Date(date).toLocaleDateString('fr-FR');

                return new Date().toLocaleDateString('fr-FR');
        },

        setIntent(resource) {
            this.intent = resource.title;
        },

		async getResources() {
            var tasksFromApi = [];

            this.isBusy = true;

            const response = await fetch('/api/resources/');
            resourcesFromApi = await response.json(); //extract JSON from the http response

						this.resources = [];

            resourcesFromApi.forEach(t => {
                this.resources.push(
							   {
								     id: t.id,
								     title: this.truncate(t.title),
                     subtitle: t.subtitle,
								     status: t.status,
								     created_on: new Date(t.created_on),
							   });
						});

            this.resources.sort(function(a, b) {
                    return b.created_on - a.created_on;
            });

            this.isBusy = false;
				},

        set_draft(draft) {
            this.draft = draft;
        }
		}
};
