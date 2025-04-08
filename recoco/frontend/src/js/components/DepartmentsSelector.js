import Alpine from 'alpinejs';

Alpine.data('DepartmentsSelector', (regions) => {
  return {
    open: false,
    territorySelectAll: true,
    regions: regions,
    init() {
      console.log(this);
    },
    async handleTerritorySelectAll() {
      this.territorySelectAll = !this.territorySelectAll;

      this.regions = this.regions.map((region) => ({
        ...region,
        active: this.territorySelectAll,
        departments: region.departments.map((department) => ({
          ...department,
          active: this.territorySelectAll,
        })),
      }));

      this.$dispatch('selected-regions', this.regions);
    },
    async handleRegionFilter(selectedRegion) {
      this.regions = this.regions.map((region) => {
        if (region.code === selectedRegion.code) {
          region.active = !region.active;
          region.departments = region.departments.map((department) => ({
            ...department,
            active: region.active,
          }));
        }

        return region;
      });

      this.territorySelectAll =
        this.regions.filter((region) => region.active).length ===
        this.regions.length;

      this.$dispatch('selected-regions', this.regions);
    },
    async handleDepartmentFilter(selectedDepartment) {
      this.regions = this.regions.map((region) => ({
        ...region,
        departments: region.departments.map((department) => {
          if (department.code === selectedDepartment.code) {
            department.active = !department.active;
          }

          return department;
        }),
        active:
          region.departments.length ===
          region.departments.filter((department) => department.active).length,
      }));

      this.territorySelectAll =
        this.regions.filter((region) => region.active).length ===
        this.regions.length;

      this.$dispatch('selected-regions', this.regions);
    },
    handleTerritorySelectAllDepartements() {
      this.territorySelectAll = !this.territorySelectAll;

      this.departments = this.departments.map((department) => ({
        ...department,
        active: this.territorySelectAll,
      }));
      this.$dispatch('selected-departments', this.departments);
    },
    handleTerritoryFilter(selectedDepartment) {
      this.departments = this.departments.map((department) => {
        if (department.code === selectedDepartment.code) {
          department.active = !department.active;
        }

        return department;
      });

      this.territorySelectAll =
        this.departments.filter((department) => department.active).length ===
        this.departments.length;

      // return (this.displayedData = this.filterProjectsByDepartments(
      //   this.searchProjects(this.search)
      // ).sort(this.currentSort));
      this.$dispatch('selected-departments', this.departments);
    },
  };
});
