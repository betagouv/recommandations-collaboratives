import switchtender from '../fixtures/users/switchtender.json'
import collectivity from '../fixtures/users/collectivity.json'

Cypress.Commands.add("login", (role) => {

    let username = ""

    switch (role) {
        case "switchtender":
            username = switchtender[0].fields.username
            break;
        case "collectivity":
            username = collectivity[0].fields.username
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
