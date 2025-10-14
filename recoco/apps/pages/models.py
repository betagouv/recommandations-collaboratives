from wagtail.admin.panels import FieldPanel
from wagtail.blocks import RichTextBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page

from .blocks import HeroBlock, MultiColumnsBlock, QuoteBlock


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


class ActualityListPage(Page):
    """List all actualities in a fancy manner"""

    subpage_types = ["ActualityPage"]


class ActualityPage(Page):
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

    quote = StreamField(
        [("quote", QuoteBlock(label="Citation"))], min_num=0, max_num=1, blank=True
    )

    content_panels = Page.content_panels + [
        FieldPanel("heading"),
        FieldPanel("gallery"),
        FieldPanel("content"),
        FieldPanel("quote"),
    ]
