function action_pusher_app() {
		return {
        isBusy: true,
        search: '',

        db: new MiniSearch({
            fields: ['title', 'subtitle', 'tags'], // fields to index for full-text search
            storeFields: ['title', 'subtitle', 'url'] //
        }),

        push_type: 'single',

        intent: '',
        content: '',

        resources: [],
        results: [],
        suggestions: [],
        selected_resource: null,
        selected_resources: [],
        public: true,
        draft: false,

        searchResources(text=null) {
            if (!text) {
                text = this.search;
            }

            this.results = this.db.search(text, { fuzzy: 0.2 }).slice(0, 8);
            this.suggestions = this.db.autoSuggest(text, { fuzzy: 0.2 }).slice(0, 2);

            return true;
        },

        resultsAndSelected() {
            if (this.push_type == 'multiple') {
                for(var resource of this.selected_resources) {
                    var f = _.find(this.resources, function(r) { return resource == r.id; });

                    /* Add it to the list of results */
                    if (! _.find(this.results, function(r) { return resource == r.id; } )) {
                        this.results.push(f);
                    }
                }
            }

            return this.results;
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

        async update_recommendation(task_id, intent, content, resource_id) {
            this.intent = intent;
            this.content = content;

            if (resource_id)
                this.push_type = 'single';
            else
                this.push_type = 'noresource';

            await this.getResources();

            if (resource_id) {
                this.results = _.where(this.resources, {'id': resource_id });

                if (this.results.length) {
                    this.selected_resource = resource_id;
                    this.selected_resources = [resource_id];
                    this.setIntent(this.results[0]);
                }
            }

        },

        async create_recommendation() {
            await this.getResources();

            const params = new URLSearchParams(document.location.search);

            const selected_resource = parseInt(params.get('resource'));

            if (selected_resource) {
                this.results = _.where(this.resources, {'id': selected_resource });
                if (this.results.length) {
                    this.selected_resource = selected_resource;
                    this.selected_resources = [selected_resource];
                    this.setIntent(this.results[0]);
                }
            }
        },

		    async getResources() {
            var tasksFromApi = [];

            this.isBusy = true;

            const response = await fetch('/api/resources/');
            resourcesFromApi = await response.json(); //extract JSON from the http response

            resourcesFromApi.forEach(t => {
                let entry = {
								    id: t.id,
								    title: t.title,
                    subtitle: t.subtitle,
                    tags: t.tags,
                    url: t.web_url
							  };

                this.resources.push(entry);
                this.db.add(entry);
						});

            this.isBusy = false;
				},

        set_draft(draft) {
            this.draft = draft;
            this.public = ! this.draft;
        }
		}
};
