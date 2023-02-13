import projects from '../../../../fixtures/projects/projects.json'
const currentProject = projects[1];

describe('I can advice a project', () => {

    beforeEach(() => {
        cy.login("jeanne");
    })

    it('goes to overview page and advise the project', () => {

        cy.visit('/projects')

        cy.contains(currentProject.fields.name).click({force:true});

        // cy.url().should('include', '/presentation')

        // cy.contains("Conseiller ce projet").click({ force: true })
        // cy.wait(500);
        // cy.contains("Ne plus conseiller ce projet")
        // cy.contains("Jeanne Conseille")
    })
})
