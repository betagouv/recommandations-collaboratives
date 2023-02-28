import projects from '../../../../fixtures/projects/projects.json'
const currentProject = projects[1];

//Must be dore after `addARecommandationAsASwitchtender.cy.js`
describe('I can comment & interact with a recommandation', () => {
    beforeEach(() => {
        cy.login("jean");
    })

    it('goes to recommandation page', () => {

        cy.visit('/projects')

        cy.contains(currentProject.fields.name).click({force:true});

        cy.contains("Recommandations").click({ force: true })

        cy.url().should('include', '/actions')

        cy.contains('Reco à modifier').parent().click({force:true});

        // const now = new Date();

        cy.get('#modal-textarea')
            .type(`test`)
            .should('have.value', `test`)

        cy.contains("Envoyer").click({ force: true })

        cy.contains(`test`)

        cy.get('#task-preview').get('[aria-label="Close"]').first().click({force:true})

        cy.wait(500)

        cy.contains('Reco à modifier').parent().click({force:true});
        cy.contains(`test`);
    })
})
