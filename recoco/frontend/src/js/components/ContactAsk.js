import Alpine from 'alpinejs';

function ContactAsk () {
  return {
    contacts:[], //tableau des contacts
    init() {
     this.contacts = JSON.parse(localStorage.getItem('contacts')) || [];
    },
    isLoaded(user) {
        for (let i = 0; i < this.contacts.length; i++) {
            if (this.contacts[i] === user) {
                return true;
            }
        }
        return false;
    },
    togglecliqueUser(user) {
        this.contacts=[...this.contacts,user];
        localStorage.setItem('contacts', JSON.stringify(this.contacts));
    },
  };
}

Alpine.data('ContactAsk', ContactAsk);
