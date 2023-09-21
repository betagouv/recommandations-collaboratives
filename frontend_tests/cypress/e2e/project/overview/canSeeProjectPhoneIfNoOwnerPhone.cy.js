import projects from '../../../fixtures/projects/projects.json'

const currentProject = projects[1];

describe('I can go to overview tab', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('see the project phone if no project owner phone number', () => {
        cy.visit(`/project/${currentProject.pk}`)

        //Used to match +33phone logic returned from django
        cy.contains(`+33${currentProject.fields.phone.replace(/\s/g, "").substring(1)}`);
    })
})
