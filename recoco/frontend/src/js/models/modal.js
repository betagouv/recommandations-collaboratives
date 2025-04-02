// Modal normalization
export const Modal = (_this) => {
  return {
    responseModal(data = null) {
      console.log('responseModal', data);
      _this.$dispatch('modal-response', data);
    },
    closeModal() {
      _this.$dispatch('modal-response', null);
    },
  };
};
