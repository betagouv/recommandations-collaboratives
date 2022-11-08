import users from '../fixtures/users/users.json'

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

Cypress.Commands.add("becomeSwitchtenderOnProject", (projectName) => {
    cy.visit('/projects')
    cy.contains(`${projectName}`).click({ force: true });

    cy.get('body').then(($body) => {
        //If we already are switchtender
        if ($body.text().includes('Ne plus conseiller le projet')) {
            return
        } else {
            cy.contains("Conseiller le projet").click({ force: true })
            cy.contains("Ne plus conseiller le projet").should('exist')
        }
    })
})
