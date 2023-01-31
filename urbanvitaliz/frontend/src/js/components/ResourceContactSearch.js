import Alpine from 'alpinejs'
import List from 'list.js'

Alpine.data("ResourceContactSearch", ResourceContactSearch)

function ResourceContactSearch(nbContacts) {
    return {
        selectedContacts: [],
        init() {

            if (!nbContacts > 0) return

            const options = {
                valueNames: ['name']
            };

            new List('contacts-list', options);

            //Get already selected items
            Array.from(this.$refs.contactsField.children.id_contacts.options).forEach(option => {
                if (option.selected) {
                    const selectedContact = {
                        name: option.innerHTML,
                        value: option.value
                    }
                    this.selectedContacts.push(selectedContact);
                }
            })

            Array.from(this.$refs.contactListWrapper.getElementsByTagName('li')).forEach(li => {
                this.selectedContacts.forEach(contact => {
                    if (li.getAttribute("id") == contact.value) {
                        li.classList.add('d-none')
                    }
                })
            })
        },
        handleAddContact(event, value, name) {
            event.target.parentNode.classList.add('d-none')
            const selectedContact = {
                name: name,
                value: value,
                element:event.target.parentNode
            }
            this.selectedContacts.push(selectedContact);

            Array.from(this.$refs.contactsField.children.id_contacts.options).forEach(option => {
                if (option.value == value) {
                    option.selected = true
                }
            })
        },
        handleRemoveContact(event, contact) {
            const removedItem = this.selectedContacts.find(item => item.value == contact.value);
            removedItem.element.classList.remove('d-none')

            event.target.parentNode.classList.remove('d-none')
            const contactFound = this.selectedContacts.indexOf(contact)
            this.selectedContacts.splice(contactFound, 1)

            Array.from(this.$refs.contactsField.children.id_contacts.options).forEach(option => {
                if (option.value == contact.value) {
                    option.selected = false
                }
            })
        }
    }
}

