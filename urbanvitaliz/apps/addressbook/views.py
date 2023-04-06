from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render, reverse
from urbanvitaliz.utils import has_perm_or_403

from . import models

########################################################################################
# Organization
########################################################################################


class OrganizationForm(forms.ModelForm):
    """Form for creating an Organization"""

    class Meta:
        model = models.Organization
        fields = ["name", "departments"]


@login_required
def organization_create(request):
    """Create a new Organization"""
    has_perm_or_403(request.user, "use_addressbook")

    if request.method == "POST":
        form = OrganizationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            departments = form.cleaned_data.get("departments")
            organization, _ = models.Organization.on_site.get_or_create(name=name)
            organization.sites.add(request.site)
            organization.departments.add(*departments)
            organization.save()
            return redirect(reverse("addressbook-organization-list"))
    else:
        form = OrganizationForm()
    return render(request, "addressbook/organization_create.html", locals())


@login_required
def organization_update(request, organization_id=None):
    """Update an Organization"""
    has_perm_or_403(request.user, "use_addressbook")

    organization = get_object_or_404(
        models.Organization, sites=request.site, pk=organization_id
    )
    if request.method == "POST":
        form = OrganizationForm(request.POST, instance=organization)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            form.save_m2m()
            return redirect(reverse("addressbook-organization-list"))
    else:
        form = OrganizationForm(instance=organization)
    return render(request, "addressbook/organization_update.html", locals())


@login_required
def organization_list(request):
    """Return the Organization list"""
    has_perm_or_403(request.user, "use_addressbook", request.site)

    organizations = models.Organization.objects.order_by("name")
    return render(request, "addressbook/organization_list.html", locals())


@login_required
def organization_details(request, organization_id):
    """Return the details for a given Organization"""
    has_perm_or_403(request.user, "use_addressbook")

    organization = get_object_or_404(
        models.Organization, sites=request.site, pk=organization_id
    )
    contacts = models.Contact.on_site.filter(organization=organization)
    return render(request, "addressbook/organization_details.html", locals())


########################################################################################
# Contact
########################################################################################


class ContactForm(forms.ModelForm):
    """Form for creating an Contact"""

    class Meta:
        model = models.Contact
        fields = [
            "first_name",
            "last_name",
            "division",
            "email",
            "phone_no",
            "mobile_no",
        ]


@login_required
def contact_create(request, organization_id: int):
    """Create a new Contact"""
    has_perm_or_403(request.user, "use_addressbook")

    organization = get_object_or_404(models.Organization, pk=organization_id)

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.organization = organization
            instance.site = request.site
            instance.save()
            return redirect(
                reverse("addressbook-organization-details", args=[organization.pk])
            )
    else:
        form = ContactForm()
    return render(request, "addressbook/contact_create.html", locals())


@login_required
def contact_update(request, contact_id=None):
    """Update a Contact"""
    has_perm_or_403(request.user, "use_addressbook")

    contact = get_object_or_404(models.Contact, site=request.site, pk=contact_id)
    if request.method == "POST":
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            next_url = reverse(
                "addressbook-organization-details", args=[contact.organization_id]
            )
            return redirect(next_url)
    else:
        form = ContactForm(instance=contact)
    return render(request, "addressbook/contact_update.html", locals())


# eof
