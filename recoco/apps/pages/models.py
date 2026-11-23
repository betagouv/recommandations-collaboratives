from django.core.exceptions import ValidationError
from django.db import models
from django.templatetags.static import static
from django.utils.html import format_html
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

    # Displayed until the editor fills the page: same content as the core homepage
    PLACEHOLDER_BASELINE = (
        "Porteurs de dossiers, recevez des conseils personnalisés "
        "des conseillers compétents."
    )
    PLACEHOLDER_STEPS = [
        (
            "search.png",
            "Icone de recherche",
            "Les porteurs décrivent leur dossier et ses besoins",
        ),
        (
            "form.png",
            "Icone d'un fichier",
            "Les conseillers compétents la guident à chaque étape",
        ),
        (
            "community.png",
            "Icone de communauté",
            "Les porteurs font avancer leur dossier",
        ),
        (
            "progress.png",
            "Icone de progrès",
            "Tous alimentent l’évolution du dossier et des besoins",
        ),
    ]

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

    hero_title = models.CharField(
        "Titre",
        max_length=255,
        blank=True,
        help_text="Si vide, le nom du site est affiché.",
    )
    hero_baseline = models.CharField(
        "Accroche",
        max_length=255,
        blank=True,
        help_text="Si vide, une accroche générique est affichée.",
    )
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Image carrée, 500×500 pixels minimum. "
        "Si vide, une illustration générique est affichée.",
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

    body = StreamField(
        HomeBodyBlock(),
        blank=True,
        verbose_name="Sections",
        help_text="Si vide, la présentation du site (description et bénéficiaires "
        "de sa configuration) et un parcours en quatre étapes sont affichés.",
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("banner_text", heading="Bandeau d’information : texte"),
                FieldPanel(
                    "banner_link_label", heading="Bandeau d’information : texte du lien"
                ),
                FieldPanel(
                    "banner_link_page", heading="Bandeau d’information : page liée"
                ),
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

    def get_placeholder_about(self, site_name, site_config):
        description = site_config.description if site_config else None
        if not description:
            return None

        text = format_html("<p>{}</p>", description)
        if site_config.target_audience:
            text = format_html(
                "{}<p>Bénéficiaires du service : {}</p>",
                text,
                site_config.target_audience,
            )
        return {
            "title": f"À propos de {site_name}",
            "text": text,
            "width": "wide",
            "alignment": "left",
            "background": "blue",
        }

    def get_placeholder_steps(self, site_name):
        return {
            "title": f"Comment fonctionne {site_name} ?",
            "background": "grey",
            "cards": [
                {
                    "icon_url": static(f"home/img/home/{icon}"),
                    "icon_alt": alt,
                    "text": text,
                }
                for icon, alt, text in self.PLACEHOLDER_STEPS
            ],
        }

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        site_name = request.site.name

        context["hero_title"] = self.hero_title or site_name
        context["hero_baseline"] = self.hero_baseline or self.PLACEHOLDER_BASELINE
        if not self.body:
            site_config = getattr(request, "site_config", None)
            context["placeholder_about"] = self.get_placeholder_about(
                site_name, site_config
            )
            context["placeholder_steps"] = self.get_placeholder_steps(site_name)

        return context

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
