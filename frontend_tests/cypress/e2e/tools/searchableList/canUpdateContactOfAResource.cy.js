import contacts from '../../../fixtures/addressbook/contacts.json'

describe('I can assign new contacts when I edit a resource', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('goes to edit a resource and assign 3 new contacts', () => {
        cy.visit('/ressource/1/')
        cy.contains('Éditer').click({force:true})

        cy.get('#id_contacts-selected-list').children().eq('1').children('span').click({force:true})
        cy.get('#id_contacts-selected-list').children().eq('1').children('span').click({force:true})
        cy.get('#id_contacts-selected-list').children().eq('1').children('span').click({force:true})

        cy.get('#id_contacts-input').focus()
        cy.get('#id_contacts-list').children().first('p').click({force:true})

        cy.get('[type="submit"]').click({ force: true });

        cy.url().should('include', '/ressource/')

        cy.contains(contacts[1].fields.first_name)
    })
})
