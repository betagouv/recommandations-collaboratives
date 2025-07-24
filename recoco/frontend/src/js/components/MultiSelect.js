document.addEventListener('alpine:init', () => {
  Alpine.data('alpineMultiSelect', (obj) => ({
    isRegion: obj.isRegion || false,
    objectsToSelect: obj.objectsToSelect || [],
    regions: [],
    options: [],
    selected: obj.selected || [],
    selectedElms: [],
    show: false,
    search: '',
    open() {
      this.show = true;
    },
    close() {
      this.show = false;
    },
    toggle() {
      this.show = !this.show;
    },
    isOpen() {
      return this.show === true;
    },
    init() {
      this.buildOptions();
      this.$watch('objectsToSelect', () => {
        console.log('objectsToSelect changed', this.objectsToSelect);
        this.buildOptions();
      });
      // searching for the given value
      this.$watch('search', (e) => {
        this.options = [];
        if (this.isRegion) {
          this.regions.forEach((region) => {
            region.departments.forEach((dep) => {
              let reg = new RegExp(this.search, 'gi');
              if (`(${dep.code}) ${dep.name}`.match(reg)) {
                this.options.push({
                  value: dep.code,
                  text: `(${dep.code}) ${dep.name}`,
                  search: `(${dep.code}) ${dep.name}`,
                  selected: this.selected.includes(dep.code),
                  region: region.name,
                });
              }
            });
          });
        } else {
          const options =
            document.getElementById(this.elementId)?.options || [];
          Object.values(options)
            .filter((el) => {
              let reg = new RegExp(this.search, 'gi');
              return el.dataset.search.match(reg);
            })
            .forEach((el) => {
              let newel = {
                value: el.value,
                text: el.innerText,
                search: el.dataset.search,
                selected: this.selected.includes(el.value),
              };
              this.options.push(newel);
            });
        }
      });
    },
    buildOptions() {
      const data = this.objectsToSelect;
      console.log('buildOptions', data);
      if (this.isRegion) {
        this.regions = data || [];
        this.options = [];
        this.regions.forEach((region) => {
          region.departments.forEach((dep) => {
            this.options.push({
              value: dep.code,
              text: `(${dep.code}) ${dep.name}`,
              search: `(${dep.code}) ${dep.name}`,
              selected: this.selected.includes(dep.code),
              region: region.name,
            });
          });
        });
        this.selectedElms = this.options.filter((opt) => opt.selected);
      } else {
        this.options = [];
        for (let i = 0; i < data.length; i++) {
          this.options.push({
            value: data[i].code,
            text: `(${data[i].code}) ${data[i].name}`,
            search: `(${data[i].code}) ${data[i].name}`,
            selected: this.selected.includes(data[i].code),
          });
          if (this.options[i].selected) {
            this.selectedElms.push(this.options[i]);
          }
        }
      }
    },
    clear() {
      this.search = '';
    },
    deselect() {
      setTimeout(() => {
        this.selected = [];
        this.selectedElms = [];
        Object.keys(this.options).forEach((key) => {
          this.options[key].selected = false;
        });
      }, 100);
    },
    select(index, event) {
      if (!this.options[index].selected) {
        this.options[index].selected = true;
        this.options[index].element = event ? event.target : null;
        this.selected.push(this.options[index].value);
        this.selectedElms.push(this.options[index]);
      } else {
        this.selected.splice(
          this.selected.lastIndexOf(this.options[index].value),
          1
        );
        this.options[index].selected = false;
        Object.keys(this.selectedElms).forEach((key) => {
          if (this.selectedElms[key].value == this.options[index].value) {
            setTimeout(() => {
              this.selectedElms.splice(key, 1);
            }, 100);
          }
        });
      }
      this.$dispatch('set-departments', this.selected);
    },
    remove(index, option) {
      this.selectedElms.splice(index, 1);
      Object.keys(this.selected).forEach((skey) => {
        if (this.selected[skey] == option.value) {
          this.selected.splice(skey, 1);
        }
      });
      Object.keys(this.options).forEach((key) => {
        if (this.options[key].value == option.value) {
          this.options[key].selected = false;
        }
      });
      this.$dispatch('set-departments', this.selected);
    },
    selectedElements() {
      return this.options.filter((op) => op.selected === true);
    },
    selectedValues() {
      return this.options
        .filter((op) => op.selected === true)
        .map((el) => el.value);
    },
    resetSelectedDepartments() {
      this.selected = [];
      this.selectedElms = [];
      Object.keys(this.options).forEach((key) => {
        this.options[key].selected = false;
      });
    },
    // Region-specific methods
    handleRegionSelect(region) {
      if (!this.isRegion) return;
      const allSelected = region.departments.every((dep) =>
        this.selected.includes(dep.code)
      );
      if (allSelected) {
        region.departments.forEach((dep) => {
          const idx = this.selected.indexOf(dep.code);
          if (idx !== -1) this.selected.splice(idx, 1);
        });
      } else {
        region.departments.forEach((dep) => {
          if (!this.selected.includes(dep.code)) {
            this.selected.push(dep.code);
          }
        });
      }
      this.selectedElms = this.options.filter((opt) =>
        this.selected.includes(opt.value)
      );
      this.$dispatch('set-departments', this.selected);
    },
    isRegionSelected(region) {
      if (!this.isRegion) return false;
      return region.departments.every((dep) =>
        this.selected.includes(dep.code)
      );
    },
    handleDepartmentSelect(dep) {
      const idx = this.selected.indexOf(dep.code);
      if (idx === -1) {
        this.selected.push(dep.code);
      } else {
        this.selected.splice(idx, 1);
      }
      this.selectedElms = this.options.filter((opt) =>
        this.selected.includes(opt.value)
      );
      this.$dispatch('set-departments', this.selected);
    },
    isDepartmentSelected(dep) {
      return this.selected.includes(dep.code);
    },
  }));
});
