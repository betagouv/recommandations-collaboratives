import Alpine from 'alpinejs';
import api, {
  contactsUrl,
  searchContactsUrl,
  getOrganizationById,
} from '../utils/api';
import _ from 'lodash';
import { formatDate } from '../utils/date';

Alpine.data('ContactBook', () => {
  return {
    formatDate,
    searchParams: {
      search: '',
      letter: null,
    },
    letters: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split(''),
    contactListGroupByNationalGroup: {},
    async init() {
      try {
        const response = await api.get(contactsUrl(25));
        this.contactListGroupByNationalGroup = this.groupContactByNationalGroup(
          response.data.results
        );
        this.getDepartmentsOrganization(this.contactListGroupByNationalGroup);
        if (sessionStorage.getItem('letter')) {
          this.loadOrganizationStartingWith(sessionStorage.getItem('letter'));
        }
      } catch (error) {
        // TODO add a toast
        console.error(error);
        throw new Error('Erreur lors de la récupération des contacts');
      }
    },
    async getDepartmentsOrganization(nationalGroupList) {
      for (const nationalGroup of nationalGroupList) {
        for (const orga of nationalGroup.organizations) {
          if (orga.id) {
            orga.departments = (
              await api.get(getOrganizationById(orga.id))
            ).data.departments;
          }
        }
      }
    },
    searchContacts(search) {
      this.searchParams.search = search;
      this.getContactData();
    },
    loadOrganizationStartingWith(letter) {
      if (letter === this.searchParams.letter) {
        return;
      }
      this.searchParams.letter = letter;
      sessionStorage.setItem('letter', letter);

      this.getContactData();
    },
    async getContactData() {
      const response = await api.get(
        searchContactsUrl(this.searchParams.search, this.searchParams.letter)
      );
      this.contactListGroupByNationalGroup = this.groupContactByNationalGroup(
        response.data.results
      );
      this.getDepartmentsOrganization(this.contactListGroupByNationalGroup);
    },

    groupContactByOrganization(contactList) {
      contactList.sort((a, b) =>
        a.organization.name.localeCompare(b.organization.name, 'en', {
          sensitivity: 'base',
        })
      );
      const contactByOrganization = _.groupBy(
        contactList,
        ({ organization: { name } }) => name
      );
      const contactByOrganizationArray = [];
      for (const key in contactByOrganization) {
        contactByOrganizationArray.push({
          name: key,
          id: contactByOrganization[key][0].organization.id,
          contacts: contactByOrganization[key],
        });
      }
      return contactByOrganizationArray;
    },

    groupContactByNationalGroup(contactList) {
      const contactByNationalGroup = _.groupBy(
        contactList,
        (contact) => contact.organization?.group?.name || 'Autres'
      );
      const contactByNationalGroupArray = [];
      for (const key in contactByNationalGroup) {
        contactByNationalGroupArray.push({
          name: key,
          id: contactByNationalGroup[key][0].organization.group?.id,
          organizations: this.groupContactByOrganization(
            contactByNationalGroup[key]
          ),
        });
      }
      contactByNationalGroupArray.sort((a, b) =>
        a.name.localeCompare(b.name, 'fr', { sensitivity: 'base' })
      );
      return contactByNationalGroupArray;
    },

    resetLetterFilter() {
      this.searchParams.letter = null;
      sessionStorage.removeItem('letter');
      this.getContactData();
    },

    deleteContact(contact) {
      api.delete(`${contactsUrl()}${contact.id}/`).then((response) => {
        location.reload();
      });
    },

    isCreateContactModalOpen: false,
    openModalCreateContact(contact = null) {
      // create contact modal
      this.isCreateContactModalOpen = true;
      if (contact) {
        this.$nextTick(() => {
          this.$dispatch('init-create-contact-modal-data', contact);
        });
      }
    },

    isCreateOrganizationModalOpen: false,
    openModalCreateOrganization(organization = null, nationalGroup = null) {
      this.isCreateOrganizationModalOpen = true;
      if (organization) {
        if (nationalGroup && nationalGroup.name !== 'Autres') {
          organization.group = nationalGroup;
        }
        this.$nextTick(() => {
          this.$dispatch('init-create-organization-modal-data', organization);
        });
      }
    },
    closeCreatesModal(event) {
      if (event.target.id == 'create-organization-modal') {
        this.isCreateOrganizationModalOpen = false;
        return;
      }
      if (event.target.id == 'create-contact-modal') {
        this.isCreateContactModalOpen = false;
        return;
      }
      return;
    },
  };
});
