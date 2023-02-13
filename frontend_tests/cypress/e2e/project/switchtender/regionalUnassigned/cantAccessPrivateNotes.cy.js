import projects from '../../../../fixtures/projects/projects.json'
const currentProject = projects[1];

describe("I can't access privates notes as a non positionned adviser", () => {

    beforeEach(() => {
        cy.login("jeannot");
    })

    it('goes to the project page and not beeing able to see the private note tab', () => {

        cy.visit('/projects')

        cy.contains(currentProject.fields.name).click({force:true});

        cy.contains("Suivi interne").should('not.exist')
    })
})
