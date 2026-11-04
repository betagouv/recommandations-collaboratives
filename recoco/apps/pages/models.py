from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.blocks import RichTextBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtail.search import index

from .blocks import HeroBlock, HomeBodyBlock, MultiColumnsBlock, QuoteBlock


class SimplePage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]


class ShowcaseListPage(Page):
    """List all show cases in a fancy manner"""

    subpage_types = ["ShowcasePage"]


class ShowcasePage(Page):
    heading = StreamField(
        [("hero", HeroBlock(label="Hero"))],
        min_num=1,
        max_num=1,
        verbose_name="En-tête",
    )

    gallery = StreamField(
        [("pictures", ImageChooserBlock())],
        min_num=1,
        max_num=3,
        verbose_name="Gallerie",
        blank=True,
    )

    content = StreamField(
        [
            ("multicol", MultiColumnsBlock(label="Multi Colonnes")),
            ("richtext", RichTextBlock(label="Texte riche")),
        ],
        verbose_name="Contenu",
    )

    quote = StreamField(
        [("quote", QuoteBlock(label="Citation"))], min_num=0, max_num=1, blank=True
    )

    content_panels = Page.content_panels + [
        FieldPanel("heading"),
        FieldPanel("gallery"),
        FieldPanel("content"),
        FieldPanel("quote"),
    ]


class NewsListPage(Page):
    """List all news articles in a fancy manner"""

    subpage_types = ["NewsPage"]


class NewsPage(Page):
    heading = StreamField(
        [("hero", HeroBlock(label="Hero"))],
        min_num=1,
        max_num=1,
        verbose_name="En-tête",
    )

    gallery = StreamField(
        [("pictures", ImageChooserBlock())],
        min_num=0,
        max_num=3,
        verbose_name="Gallerie",
        blank=True,
    )

    content = StreamField(
        [
            ("multicol", MultiColumnsBlock(label="Multi Colonnes")),
            ("richtext", RichTextBlock(label="Texte riche")),
        ],
        verbose_name="Contenu",
    )

    content_panels = Page.content_panels + [
        FieldPanel("heading"),
        FieldPanel("gallery"),
        FieldPanel("content"),
    ]


class HomePage(Page):
    """Homepage of a site: a fixed hero followed by sections ordered by the editor"""

    HERO_IMAGE_MIN_SIZE = 500

    parent_page_types = ["wagtailcore.Page"]

    banner_text = models.CharField("Texte", max_length=255, blank=True)
    banner_link_label = models.CharField("Texte du lien", max_length=255, blank=True)
    banner_link_page = models.ForeignKey(
        "wagtailcore.Page",
        verbose_name="Page liée",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    hero_title = models.CharField("Titre", max_length=255)
    hero_baseline = models.CharField("Accroche", max_length=255)
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Image",
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Image carrée, 500×500 pixels minimum.",
    )
    show_project_cta = models.BooleanField(
        "Afficher le bouton de dépôt de dossier", default=True
    )
    show_contact_cta = models.BooleanField(
        "Afficher le lien vers le formulaire de contact", default=False
    )
    cta_alternative = RichTextField(
        "Alternative aux boutons",
        blank=True,
        features=["bold", "italic", "link"],
    )

    body = StreamField(HomeBodyBlock(), blank=True, verbose_name="Sections")

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("banner_text"),
                FieldPanel("banner_link_label"),
                FieldPanel("banner_link_page"),
            ],
            heading="Bandeau d’information",
        ),
        MultiFieldPanel(
            [
                FieldPanel("hero_title"),
                FieldPanel("hero_baseline"),
                FieldPanel("hero_image"),
                FieldPanel("show_project_cta"),
                FieldPanel("show_contact_cta"),
                FieldPanel("cta_alternative"),
            ],
            heading="En-tête",
        ),
        FieldPanel("body"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("hero_title"),
        index.SearchField("hero_baseline"),
        index.SearchField("body"),
    ]

    class Meta:
        verbose_name = "Page d’accueil"
        verbose_name_plural = "Pages d’accueil"

    def clean(self):
        super().clean()
        errors = {}

        if bool(self.banner_link_label) != bool(self.banner_link_page):
            errors["banner_link_label"] = (
                "Renseignez le texte du lien et la page liée, ou aucun des deux."
            )
        if self.banner_link_label and not self.banner_text:
            errors["banner_text"] = "Le lien du bandeau doit accompagner un texte."

        if self.hero_image:
            width, height = self.hero_image.width, self.hero_image.height
            if width != height or width < self.HERO_IMAGE_MIN_SIZE:
                errors["hero_image"] = (
                    "L’image doit être carrée et mesurer au moins 500×500 pixels."
                )

        if errors:
            raise ValidationError(errors)
