import users from '../fixtures/users/users.json'
import project from '../fixtures/projects/project.json'

Cypress.Commands.add("login", (role) => {

    let username = ""

    switch (role) {
        case "jean":
            username = users[1].fields.username
            break;
        case "jeanne":
            username = users[2].fields.username
            break;
        case "jeannot":
            username = users[3].fields.username
            break;
        case "bob":
            username = users[4].fields.username
            break;
        case "boba":
            username = users[5].fields.username
            break;
        case "bobette":
            username = users[6].fields.username
            break;
        case "staff":
            username = users[0].fields.username
            break;
        default:
            break;
    }

    cy.request({ url: "/accounts/login/" }).then(response => {
        const setCookieValue = response.headers["set-cookie"][0]

        const regExp = /\=([^=]+)\;/;
        const matches = regExp.exec(setCookieValue);
        const token = matches[1]

        cy.request({
            method: "POST",
            url: "/accounts/login/",
            form: true,
            body: {
                login: username,
                password: "derpderp",
                csrfmiddlewaretoken: token
            }
        }).then(response => {
            cy.getCookie("sessionid").should("exist");
            cy.getCookie("csrftoken").should("exist");
        })
    })
})

Cypress.Commands.add('logout', () => {
    cy.get('#user-menu-button').click();
    cy.contains('Déconnexion').click({ force: true })
})

Cypress.Commands.add("createProject", (index) => {

    cy.visit('/')

    cy.get('a').should('have.class', 'fr-btn fr-text--xl custom-button').contains('Solliciter UrbanVitaliz').click({ force: true })

    cy.url().should('include', '/onboarding/')

    cy.get('#id_name')
        .type(`${project.name} ${index}`, { force: true })
        .should('have.value', `${project.name} ${index}`)

    cy.get('#input-project-address')
        .type(`${project.location}`, { force: true })
        .should('have.value', `${project.location}`)

    cy.get('[name=postcode]')
        .type(`${project.postcode}`, { force: true })
        .should('have.value', `${project.postcode}`)

    cy.get('#input-project-description')
        .type(`${project.description}`, { force: true })
        .should('have.value', `${project.description}`)

    cy.get('#id_response_1')
        .type(`${project.impediments}`, { force: true })
        .should('have.value', `${project.impediments}`)

    cy.get('#id_response_2_0')
        .check({ force: true })

    cy.document().then((doc) => {
        var iframe = doc.getElementById('id_captcha').querySelector('iframe');
        var innerDoc = iframe.contentDocument || iframe.contentWindow.document;
        innerDoc.querySelector('.recaptcha-checkbox').click()
    })

    cy.wait(500)

    cy.contains('Envoyer ma demande').click({ force: true });

    cy.contains(`${project.name} ${index}`).click({ force: true })
})

Cypress.Commands.add('becomeAdvisor', () => {
    cy.get("body").then(body => {
        if (body.find('#positioning-form').length > 0) {
            cy.contains('Conseiller le projet').click({ force: true })
        } else {
            assert.isOk('advisor', 'already advisor');
        }
    })

})

Cypress.Commands.add('createTask', (index) => {

    cy.get("body").then(body => {
        if (body.find('#create-task-button').length > 0) {
            cy.contains("Émettre une recommandation").click({ force: true })

            cy.get("#push-noresource").click({ force: true });

            cy.get('#intent')
                .type(`reco test ${index}`, { force: true })
                .should('have.value', `reco test ${index}`)

            cy.get('textarea')
                .type(`reco test from action description`, { force: true })
                .should('have.value', `reco test from action description`)

            cy.get("[type=submit]").click({ force: true });

            cy.url().should('include', '/actions')

            cy.contains('reco test from action')
        } else if (body.find('#create-task-button-bis').length > 0) {
            cy.contains("Créer une recommandation").click({ force: true })

            cy.get("#push-noresource").click({ force: true });

            cy.get('#intent')
                .type(`reco test ${index}`, { force: true })
                .should('have.value', `reco test ${index}`)

            cy.get('textarea')
                .type(`reco test from action description`, { force: true })
                .should('have.value', `reco test from action description`)

            cy.get("[type=submit]").click({ force: true });

            cy.url().should('include', '/actions')

            cy.contains('reco test from action')
        }
        else {
            assert.isOk('task', "can't create task");
        }
    })


})

Cypress.Commands.add('approveProject', (index) => {
    cy.login("staff");
    cy.visit('nimda/projects/project/')
    cy.contains(`${project.name} ${index}`).siblings('th.field-created_on.nowrap').children('a').click({ force: true });
    cy.get('#id_status').select(1)
    cy.get('#id_last_name')
        .type(`${project.last_name} ${index}`, { force: true })
        .should('have.value', `${project.last_name} ${index}`)
    cy.get('#id_first_name')
        .type(`${project.first_name} ${index}`, { force: true })
        .should('have.value', `${project.first_name} ${index}`)
    cy.contains('Enregistrer').click({ force: true })
    cy.contains('Déconnexion').click({ force: true })
    cy.visit('/')
})

Cypress.Commands.add('navigateToProject', (index) => {
    cy.visit(`/`)
    cy.get('#projects-list-button').click({ force: true })
    cy.contains(`${project.name} ${index}`).click({ force: true })
})
