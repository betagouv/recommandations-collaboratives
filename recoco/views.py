# encoding: utf-8

"""
Vues au niveau projet Recoco

created : 2026-06-23
"""

from django.shortcuts import render


def embed_test(request):
    """Page hôte affichant une iframe vers une URL configurable, pour tester l'embed."""
    target_url = request.GET.get("url", "")
    return render(request, "embed_test.html", {"target_url": target_url})


# eof
