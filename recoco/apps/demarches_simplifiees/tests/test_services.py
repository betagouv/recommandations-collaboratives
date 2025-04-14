import pytest
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from model_bakery import baker

from recoco.apps.home.models import SiteConfiguration
from recoco.apps.projects.models import Project, ProjectMember
from recoco.apps.resources.models import Resource
from recoco.apps.survey.models import (
    Answer,
    Choice,
    Question,
    QuestionSet,
    Session,
    Survey,
)

from ..models import DSMapping, DSResource
from ..services import find_ds_resource_for_project, make_ds_data_from_project


class TestfindDSResourceForProject:
    def test_no_commune(self):
        assert (
            find_ds_resource_for_project(
                project=baker.prepare(Project, commune=None),
                resource=baker.prepare(Resource),
            )
            is None
        )

    @pytest.mark.django_db
    def test_filter_dept(self):
        resource = baker.make(Resource)
        ds_resource = baker.make(
            DSResource,
            resource=resource,
            departments__code="64",
        )
        assert (
            find_ds_resource_for_project(
                project=baker.make(Project, commune__department__code="01"),
                resource=resource,
            )
            is None
        )
        assert (
            find_ds_resource_for_project(
                project=baker.make(Project, commune__department__code="64"),
                resource=resource,
            )
            == ds_resource
        )


@pytest.mark.django_db
class TestMakeDSDataFromProject:
    def test_no_ds_mapping(self):
        project = baker.make(Project)
        ds_resource = baker.make(DSResource)
        assert (
            make_ds_data_from_project(
                site=Site.objects.first(), project=project, ds_resource=ds_resource
            )
            == {}
        )

    def test_resolver(self, ds_schema_sample):
        site = Site.objects.first()
        survey = baker.make(Survey, site=site)
        baker.make(SiteConfiguration, site=site, project_survey=survey)

        project = baker.make(Project, name="Mon projet")
        session = baker.make(Session, survey=survey, project=project)
        question_set = baker.make(QuestionSet, survey=survey)

        question = baker.make(
            Question,
            text="Avez-vous déjà identifié des subventions ?",
            question_set=question_set,
        )
        answer = baker.make(
            Answer,
            session=session,
            question=question,
            comment="Non pas encore",
            signals="tag_a, tag_b",
        )

        question = baker.make(
            Question,
            text="Est-ce que le site est actuellement utilisé ?",
            question_set=question_set,
        )
        answer = baker.make(
            Answer, session=session, question=question, comment="extra comment"
        )
        choice = baker.make(Choice, question=question, text="Oui")
        answer.choices.add(choice)

        owner = baker.make(User, email="anakin.skywalker@test.com")
        owner.profile.organization_position = "Jedi"
        owner.profile.save()
        baker.make(ProjectMember, project=project, member=owner, is_owner=True)

        ds_resource = baker.make(DSResource, schema=ds_schema_sample)

        baker.make(
            DSMapping,
            ds_resource=ds_resource,
            site=site,
            enabled=True,
            mapping={
                "champ_Q2hhbXAtMjk3MTQ0NA": [
                    {"value": "project.name"},
                ],
                "champ_Q2hhbXAtMzYwNjk5NQ": [
                    {"value": "project.owner_email"},
                ],
                "champ_Q2hhbXAtODgwNDAy": [
                    {"value": "project.owner_organization_position"}
                ],
                "champ_Q2hhbXAtMjk0NTM2Mg": [
                    {"value": "project.owner.dummy"},
                ],
                "champ_Q2hhbXAtMzI5MzU1Mw": [
                    {"value": "edl.avez-vous-deja-identifie-des-subventions"}
                ],
                "champ_Q2hhbXAtMjkzNDQwMQ": [
                    {
                        "value": "edl.avez-vous-deja-identifie-des-subventions",
                        "conditions": [
                            {
                                "value": "edl.avez-vous-deja-identifie-des-subventions",
                                "tags": ["tag_a", "tag_b"],
                            }
                        ],
                    },
                ],
                "champ_Q2hhbXAtMzI3Njk1Nw": [
                    {
                        "value": "edl.avez-vous-deja-identifie-des-subventions",
                        "conditions": [
                            {
                                "value": "edl.avez-vous-deja-identifie-des-subventions",
                                "tags": ["tag_c"],
                            }
                        ],
                    },
                ],
                "champ_Q2hhbXAtMzI5MzU1NA": [
                    {"value": "edl.dummy-question-slug"},
                ],
                "champ_Q2hhbXAtMzMzNTgyNw": [
                    {"value": "raw[Non]"},
                ],
                "champ_Q2hhbXAtMzMzNTgyNQ": [
                    {"value": "edl.est-ce-que-le-site-est-actuellement-utilise"}
                ],
                "champ_Q2hhbXAtMzAyMDUwMA": [
                    {"value": "edl.est-ce-que-le-site-est-actuellement-utilise.comment"}
                ],
                "champ_Q2hhbXAtMTk3NzQ0NQ": [
                    {"value": "option[1]"},
                ],
                "champ_Q2hhbXAtMjk0NzQzNQ": [
                    {"value": "option[22]"},
                ],
                "champ_Q2hhbXAtMjkzNDM2NA": [
                    {"value": "option[dummy-value]"},
                ],
                "champ_Q2hhbXAtMzI4MDE4Mw": [
                    {
                        "value": "option[0]",
                        "conditions": [
                            {
                                "value": "edl.avez-vous-deja-identifie-des-subventions",
                                "tags": ["tag_c"],
                            }
                        ],
                    },
                    {
                        "value": "option[1]",
                        "conditions": [
                            {
                                "value": "edl.avez-vous-deja-identifie-des-subventions",
                                "tags": ["tag_a"],
                            }
                        ],
                    },
                ],
            },
        )

        data = make_ds_data_from_project(
            site=site, project=project, ds_resource=ds_resource
        )
        assert data == {
            "champ_Q2hhbXAtMjk3MTQ0NA": "Mon projet",
            "champ_Q2hhbXAtMzYwNjk5NQ": "anakin.skywalker@test.com",
            "champ_Q2hhbXAtODgwNDAy": "Jedi",
            "champ_Q2hhbXAtMzI5MzU1Mw": "Non pas encore",
            "champ_Q2hhbXAtMjkzNDQwMQ": "Non pas encore",
            "champ_Q2hhbXAtMzMzNTgyNw": "Non",
            "champ_Q2hhbXAtMzMzNTgyNQ": "Oui",
            "champ_Q2hhbXAtMzAyMDUwMA": "extra comment",
            "champ_Q2hhbXAtMTk3NzQ0NQ": "EPCI",
            "champ_Q2hhbXAtMzI4MDE4Mw": "Adaptation au changement climatique et prévention des risques naturels",
        }, print(data)
