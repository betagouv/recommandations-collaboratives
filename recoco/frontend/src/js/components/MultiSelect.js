document.addEventListener('alpine:init', () => {
  Alpine.data('alpineMultiSelect', (obj) => ({
    elementId: obj.elementId || 'select-list',
    options: [],
    selected: obj.selected || [],
    objectsToSelect: obj.objectsToSelect,
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

    // Initializing component
    init() {
      for (let i = 0; i < this.objectsToSelect.length; i++) {
        this.options.push({
          value: this.objectsToSelect[i].code,
          text: `(${this.objectsToSelect[i].code}) ${this.objectsToSelect[i].name}`,
          search: `(${this.objectsToSelect[i].code}) ${this.objectsToSelect[i].name}`,
          selected: Object.values(this.selected).includes(
            this.objectsToSelect[i].code
          ),
        });
        if (this.options[i].selected) {
          this.selectedElms.push(this.options[i]);
        }
      }
      // searching for the given value
      this.$watch('search', (e) => {
        this.options = [];
        const options = document.getElementById(this.elementId).options;
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
              selected: Object.values(this.selected).includes(el.value),
            };
            this.options.push(newel);
          });
      });
    },
    // clear search field
    clear() {
      this.search = '';
    },
    // deselect selected options
    deselect() {
      setTimeout(() => {
        this.selected = [];
        this.selectedElms = [];
        Object.keys(this.options).forEach((key) => {
          this.options[key].selected = false;
        });
      }, 100);
    },
    // select given option
    select(index, event) {
      if (!this.options[index].selected) {
        this.options[index].selected = true;
        this.options[index].element = event.target;
        this.selected.push(this.options[index].value);
        this.selectedElms.push(this.options[index]);
      } else {
        this.selected.splice(this.selected.lastIndexOf(index), 1);
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
    // remove from selected option
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
    // filter out selected elements
    selectedElements() {
      return this.options.filter((op) => op.selected === true);
    },
    // get selected values
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
  }));
});
