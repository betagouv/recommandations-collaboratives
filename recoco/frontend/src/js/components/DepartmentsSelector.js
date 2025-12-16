import Alpine from 'alpinejs';
import api, { regionsUrl, departmentsUrl } from '../utils/api';

Alpine.data(
  'DepartmentsSelector',
  (
    { listZone, selectAll, filterByRegions, selectedDepartments } = {
      selectAll: true,
    }
  ) => {
    return {
      open: false,
      territorySelectAll: true,
      regions: listZone,
      async init() {
        try {
          if (!listZone && filterByRegions) {
            this.regions = (await api.get(regionsUrl())).data.map((region) => {
              return { ...region, active: false };
            });
          } else if (!listZone && !filterByRegions) {
            this.departments = (await api.get(departmentsUrl())).data.map(
              (department) => {
                return { ...department, active: false };
              }
            );
          }
          if (selectedDepartments) {
            this.initSelectedDepartments();
          }
        } catch (error) {
          throw new Error('Error fetching regions or departments', error);
        }

        if (selectAll) {
          this.handleTerritorySelectAll(selectAll, { init: true });
        }
      },
      initSelectedDepartments() {
        if (this.regions) {
          this.regions = this.regions.map((region) => {
            return {
              ...region,
              departments: region.departments.map((department) => ({
                ...department,
                active: selectedDepartments.includes(department.code),
              })),
            };
          });
          this.regions.forEach((region) => {
            region.active =
              region.departments.length ===
              region.departments.filter((department) => department.active)
                .length;
          });
          this.territorySelectAll =
            this.regions.filter((region) => region.active).length ===
            this.regions.length;
        } else {
          this.departments = this.departments.map((department) => {
            return {
              ...department,
              active: selectedDepartments.includes(department.code),
            };
          });
        }
      },
      handleTerritorySelectAll(
        selectAll = !this.territorySelectAll,
        { init = false } = {}
      ) {
        this.territorySelectAll = selectAll;

        this.regions = this.regions.map((region) => ({
          ...region,
          active: this.territorySelectAll,
          departments: region.departments.map((department) => ({
            ...department,
            active: this.territorySelectAll,
          })),
        }));
        if (!init) {
          this.$dispatch('is-select-all-departments', this.territorySelectAll);
          this.$dispatch(
            'selected-departments',
            this.extractDepartmentFromSelectedRegions(this.regions)
          );
        }
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
      handleTerritoryFilter(selectedDepartment, isInit = false) {
        this.departments = this.departments.map((department) => {
          if (department.code === selectedDepartment.code) {
            department.active = !department.active;
          }

          return department;
        });

        this.territorySelectAll =
          this.departments.filter((department) => department.active).length ===
          this.departments.length;

        this.$dispatch('selected-departments', this.departments);
      },
    };
  }
);
