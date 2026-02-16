import Alpine from 'alpinejs';
import MiniSearch from 'minisearch';
import api, { postExternalRessourceUrl, resourcesUrl } from '../utils/api';

import { ToastType } from '../models/toastType';

Alpine.data('ActionPusher', () => {
  return {
    isBusy: true,
    isBusyExternalResource: false,
    canLoadNewExternalResource: false,
    search: '',
    message: {
      text: '',
      contact: '',
    },
    db: new MiniSearch({
      fields: ['title', 'subtitle', 'tags'], // fields to index for full-text search
      storeFields: [
        'title',
        'subtitle',
        'url',
        'embeded_url',
        'has_dsresource',
        'status',
        'category',
      ],
    }),

    push_type: 'single',

    intent: '',
    content: '',
    currentFile: '',
    isUploadedFile: false,
    fileName: '',

    resources: [],
    externalResource: [],
    externalResourceError: null,
    results: [],
    suggestions: [],
    selected_resource: false,
    selected_resources: [],
    public: true,
    draft: false,
    next: null,
    async init() {
      await this.$store.idbObjectStoreMgmt.init();
      const getAllvalue = await this.$store.idbObjectStoreMgmt.getAll();

      if (getAllvalue.length > 0) {
        // Create a DataTransfer object to set the file
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(getAllvalue[0].file);

        // Set the files to the input element
        const fileInput = document.getElementById('file-upload');
        if (fileInput) {
          fileInput.files = dataTransfer.files;
        }

        await this.$store.idbObjectStoreMgmt.delete(getAllvalue[0].id);
      }

      if (getAllvalue.length > 1) {
        this.$store.app.notification.message =
          "Dans ce formulaire, vous ne pouvez ajouter qu'un seul fichier par recommandation.";
        this.$store.app.notification.timeout = 5000;
        this.$store.app.notification.isOpen = true;
        this.$store.app.notification.type = ToastType.warning;
      }
    },
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
      Alpine.store('actionPusher').isSelectedProject = true;

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

      const response = await fetch(resourcesUrl());
      const resourcesFromApi = await response.json(); //extract JSON from the http response

      resourcesFromApi.forEach((t) => {
        let entry = {
          id: t.id,
          title: t.title,
          subtitle: t.subtitle,
          tags: t.tags,
          url: t.web_url,
          embeded_url: t.embeded_url,
          has_dsresource: t.has_dsresource,
          category: t.category ? t.category.name : null,
          status: t.status,
        };

        this.resources.push(entry);
        this.db.add(entry);
      });

      this.isBusy = false;
    },

    async postExternalResource(externalRessourceUrl) {
      this.isBusyExternalResource = true;
      this.externalResourceError = null;
      this.canLoadNewExternalResource = false;
      try {
        const response = await api.post(postExternalRessourceUrl(), {
          uri: externalRessourceUrl,
        });
        this.externalResource = [response.data];
        this.selected_resource = response.data.id;
        this.setIntent(response.data);
      } catch (error) {
        this.canLoadNewExternalResource = true;
        const errors = {
          403: "Vous n'avez pas les droits pour récupérer cette ressource externe, contactez un administrateur",
          500: "Erreur lors de la récupération de la ressource externe, merci d'essayez à nouveau plus tard",
          501: "Il n'est pas encore possible de récupérer des ressources externes sur ce site",
        };
        if (!errors[error.response.status]) {
          this.externalResourceError =
            'Erreur lors de la récupération de la ressource externe, merci de nous contacter si le problème persiste';
        }
        this.externalResourceError = errors[error.response.status];

        console.error(error);
      }
      this.isBusyExternalResource = false;
    },

    handleSetContact(contactId) {
      this.message.contact = { id: contactId };
    },
    handleSendRecommendation({ isDraft = false }) {
      this.set_draft(isDraft);
      this.$store.editor.currentMessageJSON.content =
        this.$store.editor.currentMessageJSON.content.filter(
          (node) => node.type !== 'contactCard' && node.type !== 'fileCard'
        );
      this.$store.editor.setContent(this.$store.editor.currentMessageJSON);
    },
    set_draft(draft) {
      this.draft = draft;
      this.public = !this.draft;
    },
  };
});
