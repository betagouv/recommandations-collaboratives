import Alpine from 'alpinejs';

Alpine.data(
  'DepartmentsSelector',
  (
    regions,
    { selectAll } = {
      selectedDepartments: [],
      selectAll: true,
    }
  ) => {
    return {
      open: false,
      territorySelectAll: true,
      regions: regions,
      init() {
        console.log(this.regions);
        if (selectAll) {
          this.handleTerritorySelectAll(selectAll);
        }
      },
      handleTerritorySelectAll(selectAll = !this.territorySelectAll) {
        this.territorySelectAll = selectAll;

        this.regions = this.regions.map((region) => ({
          ...region,
          active: this.territorySelectAll,
          departments: region.departments.map((department) => ({
            ...department,
            active: this.territorySelectAll,
          })),
        }));

        this.$dispatch(
          'selected-departments',
          this.extractDepartmentFromSelectedRegions(this.regions)
        );
      },
      handleRegionFilter(selectedRegion) {
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

        this.$dispatch(
          'selected-departments',
          this.extractDepartmentFromSelectedRegions(this.regions)
        );
      },
      handleDepartmentFilter(selectedDepartment) {
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

        this.$dispatch(
          'selected-departments',
          this.extractDepartmentFromSelectedRegions(this.regions)
        );
      },
      extractDepartmentFromSelectedRegions(regions) {
        const extractedDepartements = regions
          .flatMap((region) =>
            region.departments.map(
              (department) => department.active && department.code
            )
          )
          .filter((department) => department);
        return extractedDepartements;
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
  }
);
