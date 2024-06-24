from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


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
