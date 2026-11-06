import pytest
from django.core.exceptions import ValidationError
from django.utils.html import escape
from model_bakery import baker
from wagtail.blocks.stream_block import StreamBlockValidationError
from wagtail.blocks.struct_block import StructBlockValidationError
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Page
from wagtail.models import Site as WagtailSite

from recoco.apps.home.models import SiteConfiguration

from .blocks import (
    ButtonBlock,
    CarouselImageBlock,
    LinkTargetBlock,
    NewsBlock,
    ShowcaseMoreBlock,
    ShowcasesBlock,
    page_card,
)
from .models import HomePage, NewsPage, ShowcasePage, SimplePage

pytestmark = pytest.mark.django_db


@pytest.fixture
def make_image(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path

    def _make_image(filename="image.png", width=500, height=500):
        return Image.objects.create(
            title=filename,
            file=get_test_image_file(filename=filename, size=(width, height)),
        )

    return _make_image


@pytest.fixture
def root_page(db):
    return Page.get_first_root_node()


@pytest.fixture
def news_page(root_page):
    hero = {"title": "Actualité", "cta_link": "", "bg_color": ""}
    return root_page.add_child(
        instance=NewsPage(
            title="Actualité",
            slug="actualite",
            heading=[("hero", hero)],
            content=[("richtext", "<p>x</p>")],
        )
    )


def block_value(block, **kwargs):
    return block.to_python({**kwargs})


def make_home(root_page, **kwargs):
    fields = {"title": "Accueil", "hero_title": "Titre", "hero_baseline": "Accroche"}
    return HomePage(**{**fields, **kwargs})


@pytest.mark.django_db
def test_home_page_can_only_be_created_at_the_tree_root(root_page):
    assert HomePage.can_create_at(root_page)
    assert not HomePage.can_create_at(
        root_page.add_child(instance=SimplePage(title="simple"))
    )


@pytest.mark.django_db
def test_home_page_keeps_the_section_order_chosen_by_the_editor(root_page, make_image):
    paragraph = {
        "title": "T",
        "text": "<p>x</p>",
        "width": "narrow",
        "alignment": "left",
    }
    steps = {"title": "T", "cards": [{"icon": None, "text": "x"}]}
    home = make_home(
        root_page,
        hero_image=make_image(),
        body=[("steps", steps), ("paragraph", paragraph), ("paragraph", paragraph)],
    )
    root_page.add_child(instance=home)

    home = HomePage.objects.get(pk=home.pk)

    assert [b.block_type for b in home.body] == ["steps", "paragraph", "paragraph"]


@pytest.mark.parametrize(
    "size", [(500, 400), (400, 400)], ids=["not square", "too small"]
)
@pytest.mark.django_db
def test_home_page_rejects_invalid_hero_image(root_page, make_image, size):
    home = make_home(root_page, hero_image=make_image(width=size[0], height=size[1]))

    with pytest.raises(ValidationError) as error:
        home.clean()

    assert "hero_image" in error.value.message_dict


@pytest.mark.django_db
def test_home_page_accepts_square_hero_image(root_page, make_image):
    make_home(root_page, hero_image=make_image(width=600, height=600)).clean()


@pytest.mark.parametrize(
    "fields,field_in_error",
    [
        ({"banner_link_label": "Lire"}, "banner_link_label"),
        ({"banner_link_page_id": "root"}, "banner_link_label"),
    ],
    ids=["label without page", "page without label"],
)
@pytest.mark.django_db
def test_home_page_banner_link_needs_label_and_page(root_page, fields, field_in_error):
    if fields.get("banner_link_page_id") == "root":
        fields = {"banner_link_page_id": root_page.pk}
    home = make_home(root_page, banner_text="Info", **fields)

    with pytest.raises(ValidationError) as error:
        home.clean()

    assert field_in_error in error.value.message_dict


@pytest.mark.django_db
def test_home_page_banner_link_needs_text(root_page):
    home = make_home(
        root_page, banner_link_label="Lire", banner_link_page_id=root_page.pk
    )

    with pytest.raises(ValidationError) as error:
        home.clean()

    assert "banner_text" in error.value.message_dict


@pytest.mark.django_db
def test_link_target_rejects_page_and_url_together(root_page):
    block = LinkTargetBlock()
    value = block_value(block, page=root_page.pk, url="https://example.com")

    with pytest.raises(StructBlockValidationError):
        block.clean(value)


@pytest.mark.parametrize(
    "fields",
    [{"label": "Voir"}, {"url": "https://example.com"}],
    ids=["label only", "url only"],
)
def test_button_needs_label_and_target(fields):
    block = ButtonBlock()

    with pytest.raises(StructBlockValidationError):
        block.clean(block_value(block, **fields))


def test_button_can_stay_empty():
    block = ButtonBlock()

    block.clean(block_value(block))


@pytest.mark.parametrize("filename", ["image.png", "image.jpg", "IMAGE.JPEG"])
@pytest.mark.django_db
def test_carousel_accepts_png_and_jpg(make_image, filename):
    block = CarouselImageBlock()
    image = make_image(filename=filename)

    block.clean(
        block.to_python({"image": image.pk, "decorative": True, "alt_text": ""})
    )


@pytest.mark.django_db
def test_carousel_rejects_other_image_formats(make_image):
    block = CarouselImageBlock()
    image = make_image(filename="image.gif")

    with pytest.raises(StructBlockValidationError) as error:
        block.clean(
            block.to_python({"image": image.pk, "decorative": True, "alt_text": ""})
        )

    assert "image" in error.value.block_errors


def test_showcases_start_without_an_empty_selection_row():
    assert len(ShowcasesBlock().get_default()["showcases"]) == 0


def test_showcases_need_a_selection_or_a_count():
    block = ShowcasesBlock()

    with pytest.raises(StructBlockValidationError) as error:
        block.clean(block_value(block, title="T", showcases=[]))

    assert error.value.non_block_errors


def test_showcases_accept_a_count_without_selection():
    block = ShowcasesBlock()

    block.clean(block_value(block, title="T", latest_count=3, showcases=[]))


def test_showcase_more_needs_both_text_and_page():
    block = ShowcaseMoreBlock()

    with pytest.raises(StructBlockValidationError):
        block.clean(block_value(block, text="Voir plus"))


@pytest.mark.django_db
def test_news_cards_mix_typed_cards_and_news_pages(make_image, news_page):
    card = {
        "image": {"image": make_image().pk, "decorative": True, "alt_text": ""},
        "thematic": "Thème",
        "title": "Titre",
        "text": "<p>x</p>",
    }
    block = NewsBlock()
    value = block_value(
        block,
        title="T",
        cards=[
            {"type": "news_page", "value": news_page.pk},
            {"type": "card", "value": card},
        ],
    )

    cards = block.clean(value)["cards"]

    assert [c.block_type for c in cards] == ["news_page", "card"]
    assert cards[0].value.specific == news_page


@pytest.mark.django_db
def test_news_cards_are_limited_to_four(news_page):
    block = NewsBlock()
    value = block_value(
        block,
        title="T",
        cards=[{"type": "news_page", "value": news_page.pk}] * 5,
    )

    with pytest.raises(StructBlockValidationError) as error:
        block.clean(value)

    assert isinstance(error.value.block_errors["cards"], StreamBlockValidationError)


def add_child_with_hero(parent, model, title, **kwargs):
    return parent.add_child(
        instance=model(
            title=title,
            heading=[("hero", {"title": title, "text": f"{title} text"})],
            content=[("richtext", "<p>x</p>")],
            **kwargs,
        )
    )


@pytest.fixture
def home(root_page, make_image):
    return root_page.add_child(instance=make_home(root_page, hero_image=make_image()))


@pytest.fixture
def other_home(root_page, make_image):
    return root_page.add_child(
        instance=make_home(
            root_page, title="Autre", slug="autre", hero_image=make_image()
        )
    )


@pytest.fixture
def served_home(home):
    WagtailSite.objects.update(is_default_site=False)
    WagtailSite.objects.create(
        hostname="testserver", root_page=home, is_default_site=True
    )
    return home


def set_body(page, body):
    page.body = body
    page.save()
    return page


def test_page_card_uses_the_page_hero(home):
    card = page_card(add_child_with_hero(home, ShowcasePage, "Friche"))

    assert card["title"] == "Friche"
    assert card["text"] == "Friche text"
    assert card["image"] is None
    assert card["url"] is None or card["url"].endswith("/friche/")


def test_latest_showcases_only_keep_live_pages_of_the_site(home, other_home):
    older = add_child_with_hero(home, ShowcasePage, "Ancien")
    latest = add_child_with_hero(home, ShowcasePage, "Récent")
    add_child_with_hero(home, ShowcasePage, "Brouillon", live=False)
    add_child_with_hero(other_home, ShowcasePage, "Autre site")
    block = ShowcasesBlock()

    pages = block.get_showcases({"latest_count": 5, "showcases": []}, home)

    assert list(pages) == [latest, older]


def test_latest_showcases_are_limited_to_the_requested_count(home):
    add_child_with_hero(home, ShowcasePage, "Ancien")
    latest = add_child_with_hero(home, ShowcasePage, "Récent")
    block = ShowcasesBlock()

    pages = block.get_showcases({"latest_count": 1, "showcases": []}, home)

    assert list(pages) == [latest]


def test_handpicked_showcases_keep_their_order_and_stay_on_the_site(home, other_home):
    first = add_child_with_hero(home, ShowcasePage, "Premier")
    second = add_child_with_hero(home, ShowcasePage, "Second")
    draft = add_child_with_hero(home, ShowcasePage, "Brouillon", live=False)
    foreign = add_child_with_hero(other_home, ShowcasePage, "Autre site")
    block = ShowcasesBlock()

    pages = block.get_showcases(
        {"latest_count": None, "showcases": [second, foreign, draft, None, first]},
        home,
    )

    assert pages == [second, first]


def test_latest_count_takes_over_the_handpicked_selection(home):
    picked = add_child_with_hero(home, ShowcasePage, "Choisi")
    latest = add_child_with_hero(home, ShowcasePage, "Récent")
    block = ShowcasesBlock()

    pages = block.get_showcases({"latest_count": 1, "showcases": [picked]}, home)

    assert list(pages) == [latest]


@pytest.mark.django_db
def test_unsaved_homepage_shows_no_showcase(root_page, home):
    add_child_with_hero(home, ShowcasePage, "Friche")
    block = ShowcasesBlock()

    pages = block.get_showcases(
        {"latest_count": 3, "showcases": []}, make_home(root_page)
    )

    assert list(pages) == []


def test_news_cards_drop_pages_outside_the_site(home, other_home):
    local = add_child_with_hero(home, NewsPage, "Ici")
    foreign = add_child_with_hero(other_home, NewsPage, "Ailleurs")
    draft = add_child_with_hero(home, NewsPage, "Brouillon", live=False)
    block = NewsBlock()
    value = block_value(
        block,
        title="T",
        cards=[
            {"type": "news_page", "value": page.pk} for page in (foreign, local, draft)
        ],
    )

    cards = block.get_cards(value, home)

    assert [card["title"] for card in cards] == ["Ici"]


def test_home_page_renders_the_hero_and_the_sections(client, served_home):
    set_body(
        served_home,
        [
            (
                "paragraph",
                {
                    "title": "Notre mission",
                    "text": "<p>Service public</p>",
                    "width": "narrow",
                    "alignment": "center",
                },
            ),
            ("steps", {"title": "Comment ça marche", "cards": []}),
        ],
    )

    response = client.get("/p/")

    content = response.content.decode()
    assert response.status_code == 200
    assert "<h1" in content and "Titre" in content
    assert "Notre mission" in content
    assert "Service public" in content
    assert "home-page__text--center" in content
    assert "Comment ça marche" in content


def test_home_page_numbers_steps_without_image(client, served_home, make_image):
    image = make_image()
    card = {
        "icon": {"image": image, "decorative": True, "alt_text": ""},
        "number_image": None,
        "text": "Une étape",
    }
    served_home.body = [("steps", {"title": "Étapes", "cards": [card, card]})]
    served_home.save()

    content = client.get("/p/").content.decode()

    assert ">1</span>" in content
    assert ">2</span>" in content


def test_home_page_shows_banner_only_with_text(client, served_home):
    assert "hero-div__custom-banner" not in client.get("/p/").content.decode()

    served_home.banner_text = "Webinaire"
    served_home.save()

    assert "hero-div__custom-banner" in client.get("/p/").content.decode()


@pytest.mark.parametrize(
    "show,expected", [(True, True), (False, False)], ids=["shown", "hidden"]
)
def test_home_page_contact_link_follows_its_switch(client, served_home, show, expected):
    served_home.show_contact_cta = show
    served_home.save()

    content = client.get("/p/").content.decode()

    assert (
        "Nous contacter</a>" in content.split('class="hero-div"')[1].split("footer")[0]
    ) is expected


def test_home_page_hides_empty_showcase_and_news_sections(client, served_home):
    set_body(
        served_home,
        [
            ("showcases", {"title": "Exemples vides", "latest_count": 3}),
            ("news", {"title": "Actus vides", "cards": []}),
        ],
    )

    content = client.get("/p/").content.decode()

    assert "Exemples vides" not in content
    assert "Actus vides" not in content


@pytest.fixture
def empty_home(root_page):
    home = root_page.add_child(instance=HomePage(title="Accueil"))
    WagtailSite.objects.update(is_default_site=False)
    WagtailSite.objects.create(
        hostname="testserver", root_page=home, is_default_site=True
    )
    return home


def site_config(site, **kwargs):
    SiteConfiguration.objects.filter(site=site).delete()
    return baker.make(SiteConfiguration, site=site, **kwargs)


def test_empty_home_page_shows_the_site_name_and_generic_hero(
    client, current_site, empty_home
):
    content = client.get("/p/").content.decode()

    assert f'<h1 class="fr-h1">{current_site.name}</h1>' in content
    assert HomePage.PLACEHOLDER_BASELINE in content
    assert "home/img/home/image_placeholder.png" in content


def test_empty_home_page_shows_the_generic_steps(client, current_site, empty_home):
    content = client.get("/p/").content.decode()

    assert f"Comment fonctionne {current_site.name} ?" in content
    assert "home/img/home/search.png" in content
    for _icon, _alt, text in HomePage.PLACEHOLDER_STEPS:
        assert escape(text) in content


def test_empty_home_page_presents_the_site_from_its_configuration(
    client, current_site, empty_home
):
    site_config(
        current_site, description="Un service public", target_audience="Les communes"
    )

    content = client.get("/p/").content.decode()

    assert f"À propos de {current_site.name}" in content
    assert "<p>Un service public</p>" in content
    assert "Bénéficiaires du service : Les communes" in content


def test_empty_home_page_skips_the_presentation_without_description(
    client, current_site, empty_home
):
    site_config(current_site, description=None)

    content = client.get("/p/").content.decode()

    assert f"À propos de {current_site.name}" not in content


def test_site_description_is_escaped_in_the_placeholder(
    client, current_site, empty_home
):
    site_config(current_site, description="<script>alert(1)</script>")

    content = client.get("/p/").content.decode()

    assert "<script>alert(1)</script>" not in content
    assert "&lt;script&gt;alert(1)" in content


def test_filled_hero_replaces_the_placeholders(client, make_image, empty_home):
    empty_home.hero_title = "Mon titre"
    empty_home.hero_baseline = "Mon accroche"
    empty_home.hero_image = make_image()
    empty_home.save()

    content = client.get("/p/").content.decode()

    assert '<h1 class="fr-h1">Mon titre</h1>' in content
    assert "Mon accroche" in content
    assert HomePage.PLACEHOLDER_BASELINE not in content
    assert "image_placeholder.png" not in content


def test_any_section_replaces_the_placeholder_sections(
    client, current_site, empty_home
):
    site_config(current_site, description="Un service public")
    paragraph = {"title": "T", "text": "<p>x</p>", "width": "wide", "alignment": "left"}
    set_body(empty_home, [("paragraph", paragraph)])

    content = client.get("/p/").content.decode()

    assert f"À propos de {current_site.name}" not in content
    assert "Comment fonctionne" not in content
