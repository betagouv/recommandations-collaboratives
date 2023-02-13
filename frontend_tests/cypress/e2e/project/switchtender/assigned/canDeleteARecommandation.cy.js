import projects from '../../../../fixtures/projects/projects.json'
const currentProject = projects[1];
const currentTask = projects[5];

console.log('current task : ', currentTask);

describe('I can delete a recommandation', () => {
    beforeEach(() => {
        cy.login("jean");
    })

    it('goes to the recommandation tab, click on the recommandation and deletes it', () => {

        cy.visit('/projects')

        cy.contains(currentProject.fields.name).click({ force: true });

        cy.contains("Recommandations").click({ force: true })

        cy.url().should('include', '/actions')

        cy.get(`#task-${currentTask.pk}-edit-button`).click({ force: true })
        cy.get(`#task-${currentTask.pk}-delete-button`).click({ force: true })
        cy.get('#form-delete-task').contains('Supprimer').click({ force: true })
    })

    it ('checks if the recommandation is correclty deleted and not visible on the recommandation tab', () => {
        cy.visit('/projects')

        cy.contains(currentProject.fields.name).click({force:true});

        cy.contains("Recommandations").click({ force: true })

        cy.url().should('include', '/actions')

        cy.contains(currentTask.fields.intent).should('not.exist')
    }) 
})
