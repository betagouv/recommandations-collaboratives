//Must be dore after `addARecommandationAsASwitchtender.cy.js`
describe('I can comment & interact with a recommandation', () => {
    beforeEach(() => {
        cy.login("jean");
    })

    it('goes to recommandation page', () => {

        cy.visit('/projects')

        cy.contains('Friche numéro 1').click({force:true});

        cy.contains("Recommandations").click({ force: true })

        cy.url().should('include', '/actions')

        cy.contains('Ma ressource sans recommandation').parent().click({force:true});

        const now = new Date();

        cy.get('textarea')
            .type(`test : ${now}`, { force: true })
            .should('have.value', `test : ${now}`)

        cy.contains("Envoyer").click({ force: true })

        cy.contains(`test : ${now}`)

        cy.get('a').contains("En cours").click({ force: true });

        cy.get('[aria-label="Close"]').click({force:true})

        cy.wait(500)

        cy.contains('Ma ressource sans recommandation').parent().click({force:true});
        cy.contains(`test : ${now}`);
    })
})
