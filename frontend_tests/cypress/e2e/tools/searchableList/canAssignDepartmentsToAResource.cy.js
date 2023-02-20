describe('I can assign some deparments when I create a resource', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('goes to create a resource and assign 3 deparments', () => {
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

        // cy.get('#id_departments')
        //     .select(1, {force:true})

        cy.get('#id_expires_on')
            .type('20/12/2022', { force: true })
            .should('have.value', '20/12/2022')

        cy.get('[type="submit"]').click({ force: true });

        cy.url().should('include', '/ressource/')

        cy.contains("Ressource de test")
        cy.contains("résumé de la ressource de test")
    })
})
