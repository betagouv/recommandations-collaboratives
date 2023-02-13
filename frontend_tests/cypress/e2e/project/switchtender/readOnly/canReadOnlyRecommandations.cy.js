import projects from '../../../../fixtures/projects/projects.json'
const currentProject = projects[1];

describe('I can read only recommandations', () => {

    beforeEach(() => {
        cy.login("jeannot");
    })

    it('goes to recommandations and read only content', () => {

        cy.visit('/projects')

        cy.contains(currentProject.fields.name).click({force:true});

        cy.contains("Recommandations").click({ force: true })

        cy.url().should('include', '/actions')

        cy.contains("Ajouter une recommandation").should('not.exist')
    })
})
