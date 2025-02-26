import Alpine from 'alpinejs';
import api, {
  contactsUrl,
  searchContactsUrl,
  getOrganizationById,
} from '../utils/api';

Alpine.data('ContactBook', () => {
  return {
    searchParams: {
      search: '',
      letter: null,
    },
    letters: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split(''),
    contactListGroupByOrganization: {},
    async init() {
      try {
        const response = await api.get(contactsUrl(25));
        this.contactListGroupByOrganization = this.groupContactByOrganization(
          response.data.results
        );
        this.getDepartmentsOrganization(this.contactListGroupByOrganization);
      } catch (error) {
        // TODO add a toast
        console.error(error);
        throw new Error('Erreur lors de la récupération des contacts');
      }
    },
    async getDepartmentsOrganization(organizationList) {
      for (const orga of organizationList) {
        if (orga.id) {
          orga.departments = (
            await api.get(getOrganizationById(orga.id))
          ).data.departments;
        }
      }
      console.log(organizationList);
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
      this.getContactData();
    },
    async getContactData() {
      const response = await api.get(
        searchContactsUrl(this.searchParams.search, this.searchParams.letter)
      );
      this.contactListGroupByOrganization = this.groupContactByOrganization(
        response.data.results
      );
      this.getDepartmentsOrganization(this.contactListGroupByOrganization);
    },

    groupContactByOrganization(contactList) {
      const contactByOrganization = Object.groupBy(
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
  };
});
