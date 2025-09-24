import Alpine from 'alpinejs';
import Select from '../utils/select-a11y';

/**
 * Initializes the SelectSearchable Alpine.js component.
 * This component enhances the accessibility of select elements.
 * It transforms the select element into a searchable select element :
 * put x-ref="selectSearchable" on the parent's select element.
 *
 * @returns {Object} The SelectSearchable component with an init method.
 */
Alpine.data('SelectSearchable', SelectSearchable);

function SelectSearchable(params) {
  return {
    selectElIsChild: params.selectElIsChild,
    recentProjectList: [],
    recentProjectListId: [],
    init() {
      const _selectList = document.getElementById('id_project');
      this.recentProjectList = this.$store.projectQueue.get();
      this.recentProjectListId = this.recentProjectList.map((x) => x.id);
      const _selectListOptions = Array.from(_selectList.children);
      const _selectListOptionsId = _selectListOptions.map((x) => +x.value);
      _selectList.innerHTML = '';
      _selectList.appendChild(_selectListOptions.shift());

      // Add recent projects to the select list
      this.recentProjectList.forEach((project, index) => {
        if (!_selectListOptionsId.includes(project.id)) {
          return;
        }
        _selectList.appendChild(
          this.createOption(
            project.id,
            `${project.commune.name} - ${project.name}`,
            index === 0
          )
        );
      });

      // Add other projects to the select list
      _selectListOptions.forEach((option) => {
        if (this.recentProjectListId.includes(+option.value)) {
          return;
        }
        _selectList.appendChild(option);
      });

      this.generatea11ySelect();
    },
    generatea11ySelect() {
      const select = this.selectElIsChild
        ? this.$refs.selectSearchable.children
        : this.$refs.selectSearchable;

      const params = new URLSearchParams(document.location.search);
      const selected_project =
        parseInt(params.get('project_id')) || this.recentProjectListId[0];
      if (selected_project) {
        this.setSelectedProject();
      }

      Array.prototype.map.call(select, function (select) {
        return new Select(select, {}, selected_project || null);
      });
    },
    createOption(value, text, selected) {
      const option = document.createElement('option');
      option.setAttribute('data-select', 'recent_project');
      option.addEventListener('click', this.setSelectedProject);
      option.value = value;
      option.text = text;
      if (selected) {
        option.selected = true;
        this.setSelectedProject();
      }
      return option;
    },
    setSelectedProject() {
      this.$store.actionPusher.isSelectedProject = true;
    },
    resetSelectedProject() {
      this.$store.actionPusher.isSelectedProject = false;
    },
  };
}
