from recoco.apps.crm.templatetags.crm_tags import note_update_url_name


def test_note_update_url_name():
    assert note_update_url_name("organisation") == "crm-organization-note-update"
    assert note_update_url_name("Utilisateur") == "crm-user-note-update"
    assert note_update_url_name("project") == "crm-project-note-update"
    assert note_update_url_name("unknown") is None
