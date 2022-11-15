describe('I can edit a resource as a switchtender', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('edits a resource', () => {
        cy.visit('/ressource/1/')
        cy.contains('Éditer').click({ force: true })
        cy.url().should('include', '/ressource/1/update/')

        cy.get('#id_title')
            .clear({ force: true })
            .type('Nouvelle ressource de test', { force: true })
            .should('have.value', 'Nouvelle ressource de test')

        cy.get('#id_subtitle')
            .clear({ force: true })
            .type('Soustitre de la ressource de test', { force: true })
            .should('have.value', 'Soustitre de la ressource de test')

        const now = new Date();

        cy.get('#id_summary')
            .clear({ force: true })
            .type(`test : ${now}`, { force: true })
            .should('have.value', `test : ${now}`)

        cy.get('#id_tags')
            .clear({ force: true })
            .type('etiquette1', { force: true })
            .should('have.value', 'etiquette1')

        cy.get('#id_departments')
            .select(1, { force: true })

        cy.get('#id_expires_on')
            .clear({ force: true })
            .type('20/12/2022', { force: true })
            .should('have.value', '20/12/2022')

        cy.get('[type="submit"]').click({ force: true });

        cy.url().should('include', '/ressource/')

        cy.contains("Cette ressource a une date limite fixée")
        cy.contains("Nouvelle ressource de test")
        cy.contains(`test : ${now}`)
        cy.contains("Département de test numéro 2")
    })
})
