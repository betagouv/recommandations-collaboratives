import Alpine from 'alpinejs';
import { Editor } from '@tiptap/core';
import MiniSearch from 'minisearch';
import api, { postExternalRessourceUrl } from '../utils/api';

Alpine.data('ActionPusher', () => {
  return {
    isBusy: true,
    isBusyExternalResource: false,
    search: '',

    db: new MiniSearch({
      fields: ['title', 'subtitle', 'tags'], // fields to index for full-text search
      storeFields: ['title', 'subtitle', 'url', 'embeded_url', 'is_dsresource'], //
    }),

    push_type: 'single',

    intent: '',
    content: '',
    currentFile: '',
    isUploadedFile: false,
    fileName: '',

    resources: [],
    externalResource: [],
    results: [],
    suggestions: [],
    selected_resource: null,
    selected_resources: [],
    public: true,
    draft: false,
    next: null,
    searchResources(text = null) {
      if (!text) {
        text = this.search;
      }

      this.results = this.db.search(text, { fuzzy: 0.2 }).slice(0, 8);
      this.suggestions = this.db.autoSuggest(text, { fuzzy: 0.2 }).slice(0, 2);

      return true;
    },

    truncate(input, size = 30) {
      return input.length > size ? `${input.substring(0, size)}...` : input;
    },
    handleFileUpload() {
      if (this.$refs.fileUploadInput.files.length > 0) {
        this.fileName = this.$refs.fileUploadInput.files[0].name;
      }
    },

    formatDateDisplay(date) {
      if (this.dateDisplay === 'toDateString')
        return new Date(date).toDateString();
      if (this.dateDisplay === 'toLocaleDateString')
        return new Date(date).toLocaleDateString('fr-FR');

      return new Date().toLocaleDateString('fr-FR');
    },

    setIntent(resource) {
      this.intent = resource.title;
    },

    async update_recommendation(task_id, intent, content, resource_id) {
      this.intent = intent;
      this.content = content;

      if (resource_id) this.push_type = 'single';
      else this.push_type = 'noresource';
      await this.getResources();

      if (resource_id) {
        // this.results = _.where(this.resources, { id: resource_id });
        this.results = this.resources.filter(
          (resource) => resource.id === resource_id
        );

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

      const selected_resource = parseInt(params.get('resource_id'));

      if (selected_resource) {
        // this.results = _.where(this.resources, { id: selected_resource });
        this.results = this.resources.filter(
          (resource) => resource.id === selected_resource
        );
        if (this.results.length) {
          this.selected_resource = selected_resource;
          this.selected_resources = [selected_resource];
          this.setIntent(this.results[0]);
        }
      }
    },

    async getResources() {
      this.isBusy = true;

      const response = await fetch('/api/resources/');
      const resourcesFromApi = await response.json(); //extract JSON from the http response

      resourcesFromApi.forEach((t) => {
        let entry = {
          id: t.id,
          title: t.title,
          subtitle: t.subtitle,
          tags: t.tags,
          url: t.web_url,
          embeded_url: t.embeded_url,
          is_dsresource: t.is_dsresource,
          category: t.category,
        };

        this.resources.push(entry);
        this.db.add(entry);
      });

      this.isBusy = false;
    },

    async postExternalResource(externalRessourceUrl) {
      this.isBusyExternalResource = true;
      try {
        const response = await api.post(postExternalRessourceUrl(), {
          uri: externalRessourceUrl,
        });
        this.externalResource = [response.data];
        this.isBusyExternalResource = false;
      } catch (error) {
        debugger;
        console.error(error);
      }
    },

    set_draft(draft) {
      this.draft = draft;
      this.public = !this.draft;
    },
  };
});
