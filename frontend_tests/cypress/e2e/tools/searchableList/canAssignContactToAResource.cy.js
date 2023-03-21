import contacts from '../../../fixtures/addressbook/contacts.json'

describe('I can assign some contacts when I create a resource', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('goes to create a resource and assign 3 contacts', () => {
        cy.visit('/ressource/create/')

        cy.get('#id_title')
            .type('Ressource de test', { force: true })
            .should('have.value', 'Ressource de test')

        cy.get('#id_subtitle')
            .type('Soustitre de la ressource de test', { force: true })
            .should('have.value', 'Soustitre de la ressource de test')

        cy.get('#id_summary')
            .type('résumé de la ressource de test', { force: true })
            .should('have.value', 'résumé de la ressource de test')

        cy.get('#id_tags')
            .type('etiquette1', { force: true })
            .should('have.value', 'etiquette1')

        cy.get('#id_contacts-input').focus()
        cy.get('#id_contacts-list').children().first('p').click({force:true})

        cy.get('#id_contacts-input').focus()
        cy.get('#id_contacts-list').children().eq('1').children().first().click({force:true})

        cy.get('#id_contacts-input').focus()
        cy.get('#id_contacts-list').children().eq('2').children().first().click({force:true})

        cy.get('#id_expires_on')
            .type('20/12/2022', { force: true })
            .should('have.value', '20/12/2022')

        cy.get('[type="submit"]').click({ force: true });

        cy.url().should('include', '/ressource/')

        cy.contains("Ressource de test")
        cy.contains("résumé de la ressource de test")

        cy.contains(contacts[1].fields.first_name)
        cy.contains(contacts[2].fields.first_name)
        cy.contains(contacts[3].fields.first_name)
    })
})
