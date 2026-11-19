import Alpine from 'alpinejs';

Alpine.data('MenuProjects', (isCollectivity = false) => {
  return {
    rawProjectList: [],
    displayedProjectList: [],
    maxDisplayedProject: 5,
    currentProject: null,
    isProjectLoading: true,
    async getProjetctsData() {
      let projectList = this.$store.projectQueue.get();

      if (isCollectivity) {
        projectList = (await this.$store.projects.getUserProjetsStatus()).map(
          (x) => x.project
        );
      }
      this.rawProjectList = [...projectList];

      const params = new URLSearchParams(document.location.search);
      const selectedProjectId = parseInt(params.get('project_id'));
      if (selectedProjectId) {
        const project = this.rawProjectList.find(
          (p) => p.id === selectedProjectId
        );
        this.currentProject = project;
      }

      this.displayedProjectList = this.rawProjectList.splice(
        0,
        this.maxDisplayedProject + 1
      );
      this.isProjectLoading = false;
    },
    sortByRecentlyVisitedProjects() {
      this.$store.projectQueue.get().forEach((projectId) => {
        const project = this.rawProjectList.find((p) => p.pk === projectId);
        if (project) {
          this.displayedProjectList.unshift(project);
        }
      });
      this.isProjectLoading = false;
    },
  };
});
