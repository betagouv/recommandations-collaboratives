import Alpine from 'alpinejs';
// import Fuse from 'fuse.js';

Alpine.data('MenuProjects', (isCollectivity = false) => {
  return {
    rawProjectList: [],
    displayedProjectList: [],
    maxDisplayedProject: 5,
    currentProject: null,
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
      // const fuseOptions = {
      //   keys: [
      //     'name',
      //     'commune.name',
      //     'commune.insee',
      //     'commune.department.name',
      //   ],
      //   isCaseSensitive: false,
      //   minMatchCharLength: 1,
      //   threshold: 0.3,
      //   findAllMatches: true,
      //   ignoreLocation: true,
      // };
      // this.fuse = new Fuse(this.rawProjectList, fuseOptions);

      this.displayedProjectList = this.rawProjectList.splice(
        0,
        this.maxDisplayedProject + 1
      );
    },
    sortByRecentlyVisitedProjects() {
      this.$store.projectQueue.get().forEach((projectId) => {
        const project = this.rawProjectList.find((p) => p.pk === projectId);
        if (project) {
          this.displayedProjectList.unshift(project);
        }
      });
      // this.rawProjectList.forEach((project) => {
      //   if (!this.displayedProjectList.includes(project)) {
      //     this.displayedProjectList.push(project);
      //   }
      // });
    },
    // onSearch() {
    //   this.filterProjects(this.search);
    // },
    // filterProjects(search) {
    //   if (search === '') {
    //     this.displayedProjectList = [...this.rawProjectList];
    //     return;
    //   }
    //   const filtered = this.fuse.search(search).map((r) => r.item);
    //   this.displayedProjectList = [...filtered];
    // },
  };
});
