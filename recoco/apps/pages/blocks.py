import os

from django.apps import apps
from django.core.exceptions import ValidationError
from wagtail import blocks
from wagtail.blocks.struct_block import StructBlockValidationError
from wagtail.images.blocks import ImageBlock, ImageChooserBlock


class HeroBlock(blocks.StructBlock):
    """
    Partly Stolen from betagouv/content-manager
    """

    bg_image = ImageChooserBlock(label="Image d’arrière plan", required=False)
    bg_color = blocks.RegexBlock(
        label="Couleur d’arrière plan au format hexa (Ex: #f5f5fe)",
        regex=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
        error_messages={
            "invalid": "La couleur n’est pas correcte, le format doit être #fff ou #f5f5fe"
        },
        required=False,
    )
    title = blocks.CharBlock(label="Titre")
    text = blocks.CharBlock(label="Texte", required=False)
    cta_label = blocks.CharBlock(label="Texte du bouton", required=False)
    cta_link = blocks.URLBlock(label="Lien du bouton", required=False)
    darken = blocks.BooleanBlock(label="Assombrir", required=False)


class ColumnBlock(blocks.StructBlock):
    text = blocks.RichTextBlock(label="Texte avec mise en forme")


class MultiColumnsBlock(blocks.StreamBlock):
    title = blocks.CharBlock(label="Titre", required=False)
    columns = ColumnBlock(label="Colonne")

    class Meta:
        block_counts = {
            "title": {"min_num": 0, "max_num": 1},
        }


class QuoteBlock(blocks.StructBlock):
    image = ImageChooserBlock(label="Illustration (à gauche)", required=False)
    quote = blocks.TextBlock(label="Citation")
    author_name = blocks.CharBlock(label="Nom de l’auteur")
    author_title = blocks.CharBlock(label="Titre de l’auteur")


# Homepage ###################################################################


BACKGROUND_CHOICES = [("white", "Blanc"), ("grey", "Gris"), ("blue", "Bleu")]


def background_block(default):
    """Background of a homepage section, chosen by the editor"""
    return blocks.ChoiceBlock(label="Fond", choices=BACKGROUND_CHOICES, default=default)


def site_pages(model_name, home):
    """Return the live pages of a model published under the given homepage

    Choosers list the pages of every site, so nothing is displayed without this
    scoping. A homepage not yet saved has no position in the tree, hence no pages.
    """
    model = apps.get_model("pages", model_name)
    if home is None or home.pk is None:
        return model.objects.none()
    return model.objects.live().descendant_of(home)


def page_card(page):
    """Return the content of a card for a page having a hero heading"""
    hero = page.heading[0].value if page.heading else {}
    image = hero.get("bg_image")
    if image:
        # the card title sits next to it and the card opens the page
        image.decorative = True
    return {
        "title": page.title,
        "text": hero.get("text"),
        "image": image,
        "url": page.url,
    }


class LinkValue(blocks.StructValue):
    @property
    def href(self):
        if self.get("url"):
            return self["url"]
        page = self.get("page")
        return page.url if page else None

    @property
    def is_external(self):
        return bool(self.get("url"))


class LinkTargetBlock(blocks.StructBlock):
    """An optional link, either to a page of the CMS or to an external URL"""

    page = blocks.PageChooserBlock(label="Page du site", required=False)
    url = blocks.URLBlock(label="Lien externe", required=False)

    def clean(self, value):
        cleaned = super().clean(value)
        if cleaned.get("page") and cleaned.get("url"):
            raise StructBlockValidationError(
                non_block_errors=[
                    ValidationError(
                        "Choisissez une page ou un lien externe, pas les deux."
                    )
                ]
            )
        return cleaned

    class Meta:
        value_class = LinkValue


class ButtonBlock(LinkTargetBlock):
    """An optional button: leave everything empty to hide it"""

    label = blocks.CharBlock(label="Texte du bouton", required=False)

    def clean(self, value):
        cleaned = super().clean(value)
        has_target = cleaned.get("page") or cleaned.get("url")
        if cleaned.get("label") and not has_target:
            raise StructBlockValidationError(
                block_errors={
                    "label": ValidationError("Le bouton doit pointer vers un lien.")
                }
            )
        if has_target and not cleaned.get("label"):
            raise StructBlockValidationError(
                block_errors={
                    "label": ValidationError("Le bouton doit avoir un texte.")
                }
            )
        return cleaned


class ParagraphBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre")
    text = blocks.RichTextBlock(label="Texte")
    side_image = ImageBlock(label="Image sur le côté", required=False)
    button = ButtonBlock(label="Bouton", required=False)
    width = blocks.ChoiceBlock(
        label="Marges",
        choices=[("wide", "Larges"), ("narrow", "Étroites")],
        default="wide",
    )
    alignment = blocks.ChoiceBlock(
        label="Justification",
        choices=[
            ("left", "Gauche"),
            ("center", "Centré"),
            ("right", "Droite"),
            ("justify", "Justifié"),
        ],
        default="left",
    )
    background = background_block("blue")

    class Meta:
        template = "pages/blocks/home/paragraph.html"


class CarouselImageBlock(ImageBlock):
    ALLOWED_EXTENSIONS = (".png", ".jpg", ".jpeg")

    def clean(self, value):
        image = super().clean(value)
        extension = os.path.splitext(image.file.name)[1].lower()
        if extension not in self.ALLOWED_EXTENSIONS:
            raise StructBlockValidationError(
                block_errors={
                    "image": ValidationError(
                        "Seules les images PNG et JPG sont acceptées."
                    )
                }
            )
        return image


class CarouselBlock(blocks.StructBlock):
    images = blocks.ListBlock(
        CarouselImageBlock(label="Image"), label="Images", min_num=1
    )
    background = background_block("white")

    class Meta:
        template = "pages/blocks/home/carousel.html"


class StepCardBlock(blocks.StructBlock):
    icon = ImageBlock(label="Icône")
    number_image = ImageBlock(
        label="Image du numéro",
        required=False,
        help_text="Sans image, le numéro de l’étape est affiché en texte.",
    )
    text = blocks.CharBlock(label="Texte")


class StepsBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre")
    cards = blocks.ListBlock(
        StepCardBlock(label="Étape"), label="Étapes", min_num=1, max_num=4
    )
    background = background_block("white")

    class Meta:
        template = "pages/blocks/home/steps.html"


class ShowcaseMoreBlock(blocks.StructBlock):
    """Closes the showcase section: leave everything empty to hide it"""

    text = blocks.CharBlock(label="Texte", required=False)
    list_page = blocks.PageChooserBlock(
        label="Page de liste",
        page_type="pages.ShowcaseListPage",
        required=False,
    )

    def clean(self, value):
        cleaned = super().clean(value)
        if bool(cleaned.get("text")) != bool(cleaned.get("list_page")):
            raise StructBlockValidationError(
                non_block_errors=[
                    ValidationError(
                        "Renseignez le texte et la page de liste, ou aucun des deux."
                    )
                ]
            )
        return cleaned


class ShowcasesBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre")
    latest_count = blocks.IntegerBlock(
        label="Nombre de réalisations récentes",
        required=False,
        min_value=1,
        help_text="Si renseigné, remplace la sélection manuelle.",
    )
    showcases = blocks.ListBlock(
        blocks.PageChooserBlock(label="Réalisation", page_type="pages.ShowcasePage"),
        label="Sélection manuelle",
        default=[],
    )
    more = ShowcaseMoreBlock(label="Encart « voir plus »", required=False)
    background = background_block("grey")

    def clean(self, value):
        cleaned = super().clean(value)
        if not cleaned.get("latest_count") and not cleaned.get("showcases"):
            raise StructBlockValidationError(
                non_block_errors=[
                    ValidationError(
                        "Sélectionnez des réalisations ou indiquez combien afficher."
                    )
                ]
            )
        return cleaned

    def get_showcases(self, value, home):
        pages = site_pages("ShowcasePage", home)
        if value["latest_count"]:
            return pages.order_by("-first_published_at")[: value["latest_count"]]

        allowed = set(pages.values_list("pk", flat=True))
        return [page for page in value["showcases"] if page and page.pk in allowed]

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        home = (parent_context or {}).get("page")
        context["cards"] = [page_card(page) for page in self.get_showcases(value, home)]
        return context

    class Meta:
        template = "pages/blocks/home/showcases.html"


class NewsCardBlock(blocks.StructBlock):
    image = ImageBlock(label="Image")
    thematic = blocks.CharBlock(label="Thématique")
    title = blocks.CharBlock(label="Titre")
    text = blocks.RichTextBlock(label="Texte")
    link = LinkTargetBlock(label="Lien", required=False)

    @staticmethod
    def as_card(value):
        return {
            "title": value["title"],
            "text": value["text"],
            "image": value["image"],
            "thematic": value["thematic"],
            "url": value["link"].href,
            "is_external": value["link"].is_external,
        }


class NewsBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre")
    cards = blocks.StreamBlock(
        [
            ("card", NewsCardBlock(label="Actualité saisie")),
            (
                "news_page",
                blocks.PageChooserBlock(
                    label="Page d’actualité", page_type="pages.NewsPage"
                ),
            ),
        ],
        label="Actualités",
        min_num=1,
        max_num=4,
    )
    background = background_block("blue")

    def get_cards(self, value, home):
        allowed = set(site_pages("NewsPage", home).values_list("pk", flat=True))
        cards = []
        for card in value["cards"]:
            if card.block_type == "card":
                cards.append(NewsCardBlock.as_card(card.value))
            elif card.value and card.value.pk in allowed:
                cards.append(page_card(card.value))
        return cards

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context["cards"] = self.get_cards(value, (parent_context or {}).get("page"))
        return context

    class Meta:
        template = "pages/blocks/home/news.html"


class HomeBodyBlock(blocks.StreamBlock):
    """Everything under the hero, in the order chosen by the editor"""

    paragraph = ParagraphBlock(label="Paragraphe")
    carousel = CarouselBlock(label="Carrousel")
    steps = StepsBlock(label="Étapes")
    showcases = ShowcasesBlock(label="Réalisations")
    news = NewsBlock(label="Actualités")
