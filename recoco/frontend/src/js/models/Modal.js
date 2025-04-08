// Modal normalization
export const Modal = (_this, identifier) => {
  return {
    id: identifier,
    responseModal(data = null) {
      _this.$dispatch('modal-response', data);
    },
    closeModal() {
      _this.$dispatch('modal-response', null);
    },
  };
};
