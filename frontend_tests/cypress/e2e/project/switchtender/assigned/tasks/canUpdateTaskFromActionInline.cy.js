import projects from '../../../../../fixtures/projects/projects.json'
const currentProject = projects[1];
const currentTask = projects[projects.length - 1];

describe('I can create a recommandation with no resource as a switcthender from the action view', () => {
    beforeEach(() => {
        cy.login("jean");
    })

    it('creates a reco from action view', () => {

        cy.visit('/projects')

        cy.contains(currentProject.fields.name).click({ force: true });

        cy.contains("Recommandations").click({ force: true })

        cy.url().should('include', '/actions')

        cy.get('#tasks-inline-button').click({force:true});
        cy.url().should('include', '/actions/inline')

        cy.get('#update-task-action-inline').click({force:true});

        cy.get('#intent')
            .clear({ force: true })
            .type('reco test from action inline updated', { force: true })
            .should('have.value', 'reco test from action inline updated')

        cy.contains("Publier").click({ force: true });

        cy.url().should('include', '/actions/inline')

        cy.contains('reco test from action inline updated')
    })
})
