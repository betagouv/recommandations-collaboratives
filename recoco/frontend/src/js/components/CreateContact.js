import Alpine from 'alpinejs';

function CreateContact() {
  return {
    modalCreateContact : null,
    modalSearchContact : null,
    contactLastName: '',
    contactFirstName: '',
    contactJob: '',
    contactEmail: '',
    contactTel: '',
    contactPhone: '',
    init() {
    },
    closeCreateContactModal() {
        this.modalCreateContact = document.querySelector('#create-contact-modal');
        this.modalCreateContact.classList.toggle('d-none');
        this.reOpenModalSearchContact();
    },
    reOpenModalSearchContact() {
        this.modalSearchContact = document.querySelector('#search-contact-modal');
        this.modalSearchContact.classList.toggle('d-none');
    },
    createContact() {
      alert('createContact');
    }
  };
}

Alpine.data('CreateContact', CreateContact);
