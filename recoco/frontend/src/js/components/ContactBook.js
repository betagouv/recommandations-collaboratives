import Alpine from 'alpinejs';
import api, {
  contactsUrl,
  contactUrl,
  searchContactsUrl,
  getOrganizationById,
} from '../utils/api';
import _ from 'lodash';
import { formatDate } from '../utils/date';
import { ToastType } from '../models/toastType';

Alpine.data('ContactBook', (departments, regions) => {
  return {
    formatDate,
    searchParams: {
      search: '',
      letter: null,
      searchDepartment: [],
    },
    isSelectAllDepartments: true,
    letters: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split(''),
    contactListGroupByNationalGroup: [],
    departments: JSON.parse(departments.textContent),
    regions: JSON.parse(regions.textContent),
    contactSearched: [],
    isContactDataLoaded: false,
    async init() {
      try {
        const response = await api.get(contactsUrl());
        this.contactListGroupByNationalGroup = this.groupContactByNationalGroup(
          response.data.results
        );
        this.initScrollToLoadOrganizationDepartments();
        if (sessionStorage.getItem('letter')) {
          this.loadOrganizationStartingWith(sessionStorage.getItem('letter'));
        }
        this.isContactDataLoaded = true;
      } catch (error) {
        this.$store.app.displayToastMessage({
          message: `Erreur lors de la récupération des contacts`,
          timeout: 5000,
          type: ToastType.error,
        });
        this.isContactDataLoaded = true;
        throw new Error('Error while fetching contacts', { cause: error });
      }
    },
    initScrollToLoadOrganizationDepartments() {
      requestAnimationFrame(() => {
        const observer = new IntersectionObserver((entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              console.log('entry.target', entry.target);
              const organizationId = entry.target.getAttribute(
                'data-organization-id'
              );
              this.getDepartmentsOrganization(organizationId);
            }
          });
        });
        const organizationContainers = document.querySelectorAll(
          '.organization-container'
        );
        organizationContainers.forEach((organizationContainer) => {
          observer.observe(organizationContainer);
        });
      });
    },
    async getDepartmentsOrganization(organizationId) {
      this.contactListGroupByNationalGroup.forEach((nationalGroup) =>
        nationalGroup.organizations.forEach(async (organization) => {
          if (
            organization.id == organizationId &&
            organization.departments == undefined
          ) {
            const response = await api.get(getOrganizationById(organizationId));
            organization.departments = response.data.departments;
          }
        })
      );
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
      if (this.isSelectAllDepartments) {
        this.searchParams.searchDepartment = [];
      }
      const response = await api.get(
        searchContactsUrl(
          this.searchParams.search,
          this.searchParams.letter,
          this.searchParams.searchDepartment
        )
      );
      if (this.searchParams.search && this.searchParams.search !== '') {
        this.contactSearched = response.data.results;
      } else {
        this.contactListGroupByNationalGroup = this.groupContactByNationalGroup(
          response.data.results
        );
        this.initScrollToLoadOrganizationDepartments();
      }
    },

    groupContactByOrganization(contactList) {
      contactList.sort((a, b) =>
        a.organization.name.localeCompare(b.organization.name, 'fr', {
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
      contactByNationalGroupArray.sort((a, b) => {
        if (a.name === 'Autres') {
          return 1;
        }
        if (b.name === 'Autres') {
          return -1;
        }
        return a.name.localeCompare(b.name, 'fr', { sensitivity: 'base' });
      });
      return contactByNationalGroupArray;
    },

    resetLetterFilter(withReloadContact = true) {
      this.searchParams.letter = null;
      sessionStorage.removeItem('letter');
      if (withReloadContact) {
        this.getContactData();
      }
    },

    deleteContact(contact) {
      api.delete(`${contactUrl(contact.id)}`).then((response) => {
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
        window.location.reload();
        // TODO: insert new contact in the contact list
        // this.insertNewContact(event.detail);
        this.isCreateContactModalOpen = false;

        return;
      }
      return;
    },
    insertNewContact(event) {
      this.contactListGroupByNationalGroup.push(newContact);
      // this.getDepartmentsOrganization(this.contactListGroupByNationalGroup);
    },
    saveSelectedDepartment(event) {
      if (!event.detail || !this.isContactDataLoaded) return;
      this.searchParams.searchDepartment = [...event.detail];
      this.getContactData();
    },
  };
});
