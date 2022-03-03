function action_pusher_app() {
		return {
        isBusy: true,
        search: '',
        resources: [],

        db: new MiniSearch({
            fields: ['title', 'subtitle', 'tags'], // fields to index for full-text search
            storeFields: ['title', 'subtitle'] //
        }),

        push_type: 'single',

        intent: '',
        content: '',

        results: [],
        suggestions: [],
        selected_resource: null,
        selected_resources: [],
        draft: false,

        searchResources() {
            this.suggestions = this.db.autoSuggest(this.search, { fuzzy: 0.2 }).slice(0, 2);
            this.results = this.db.search(this.search, { fuzzy: 0.2 }).slice(0, 8);
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
                this.db.add(
							   {
								     id: t.id,
								     title: this.truncate(t.title),
                     subtitle: t.subtitle,
                     tags: t.tags,
							   });
						});

            this.isBusy = false;
				},

        set_draft(draft) {
            this.draft = draft;
        }
		}
};
