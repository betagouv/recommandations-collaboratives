from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page

# from wagtail.fields import StreamField
# from wagtail.blocks import RichTextBlock
# from wagtail.images.blocks import ImageChooserBlock

# from .blocks import HeroBlock, MultiColumnsBlock, QuoteBlock


class SimplePage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]


# class ShowcasePage(Page):
#     heading = StreamField(
#         [("hero", HeroBlock(label="Hero"))],
#         min_num=1,
#         max_num=1,
#         verbose_name="En-tête",
#     )

#     gallery = StreamField(
#         [("pictures", ImageChooserBlock())],
#         min_num=1,
#         max_num=3,
#         verbose_name="Gallerie",
#     )

#     content = StreamField(
#         [
#             ("multicol", MultiColumnsBlock(label="Multi Colonnes")),
#             ("richtext", RichTextBlock(label="Texte riche")),
#         ],
#         verbose_name="Contenu",
#     )

#     quote = StreamField([("quote", QuoteBlock(label="Citation"))], blank=False)

#     content_panels = Page.content_panels + [
#         FieldPanel("heading"),
#         FieldPanel("gallery"),
#         FieldPanel("content"),
#         FieldPanel("quote"),
#     ]
