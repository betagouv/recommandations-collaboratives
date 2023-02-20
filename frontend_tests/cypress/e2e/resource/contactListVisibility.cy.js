import resource from '../../fixtures/resources/resources.json'
import contacts from '../../fixtures/addressbook/contacts.json'

const currentResource = resource[2]

describe('I can see the resource contact list if im logged', () => {
    beforeEach(() => {
        cy.login("bob");
    })

    it('see the contact list', () => {
        cy.visit(`/ressource/${currentResource.pk}/`)

        cy.contains(contacts[1].fields.first_name)
        cy.contains(contacts[2].fields.first_name)
        cy.contains(contacts[3].fields.first_name)
    })
})

describe("I can't see the resource contact list if im not logged", () => {
    beforeEach(() => {
    })

    it('cannot see a contact list', () => {
        cy.visit('/ressource/3/')
        cy.contains("contacts associés à cette ressource. Si vous souhaitez y accéder, veuillez vous identifier.");
    })
})
