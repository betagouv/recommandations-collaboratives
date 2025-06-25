import Alpine from 'alpinejs';

Alpine.data('AdvisorDemandValidation', () => {
  return {
    isSelectDepartments: false,
    selectedDepartmentsFromMultiSelect: [],
    init() {
    },
    handleDepartmentsSelection(departments) {
        this.selectedDepartmentsFromMultiSelect = departments;
    },
  };
});
