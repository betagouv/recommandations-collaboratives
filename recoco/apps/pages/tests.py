import pytest
from django.core.exceptions import ValidationError
from wagtail.blocks.stream_block import StreamBlockValidationError
from wagtail.blocks.struct_block import StructBlockValidationError
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Page

from .blocks import (
    ButtonBlock,
    CarouselImageBlock,
    LinkTargetBlock,
    NewsBlock,
    ShowcaseMoreBlock,
    ShowcasesBlock,
)
from .models import HomePage, NewsPage, SimplePage


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
