import Alpine from 'alpinejs';
import Select from '../utils/select-a11y';

Alpine.data('SelectSearchable', SelectSearchable);

function SelectSearchable() {
  return {
    init() {
      const select = this.$refs.selectSearchable.children;

      Array.prototype.map.call(select, function (select) {
        return new Select(select);
      });
    },
  };
}
