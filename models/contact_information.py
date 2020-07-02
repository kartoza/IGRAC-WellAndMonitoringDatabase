from django.contrib.gis.db import models
from gwml2.models.universal import GWTerm


class CIRoleTerm(GWTerm):
    """
    Function performed by the responsible party.
    """
    pass


class CIOnlineFunctionTerm(GWTerm):
    """
    Function performed by the responsible party.
    """
    pass


class CITelephone(models.Model):
    """
    Telephone numbers for contacting the responsible individual or organization.
    """
    voice = models.TextField(
        null=True, blank=True,
        verbose_name="Voice")
    facsimile = models.TextField(
        null=True, blank=True,
        verbose_name="Facsimile")


class CIAddress(models.Model):
    """
    Location of the responsible individual or organization.
    """
    delivery_point = models.TextField(
        null=True, blank=True,
        verbose_name="DeliveryPoint")
    city = models.TextField(
        null=True, blank=True,
        verbose_name="City")
    administrative_area = models.TextField(
        null=True, blank=True,
        verbose_name="AdministrativeArea")
    postal_code = models.TextField(
        null=True, blank=True,
        verbose_name="PostalCode")
    country = models.TextField(
        null=True, blank=True,
        verbose_name="Country")
    electronic_mail_address = models.TextField(
        null=True, blank=True,
        verbose_name="ElectronicMailAddress")


class CIOnlineResource(models.Model):
    """
    Information about on-line sources from which the dataset,
    specification, or community profile name and extended metadata
    elements can be obtained.
    """
    linkage = models.TextField(
        null=True, blank=True,
        verbose_name="Linkage")
    protocol = models.TextField(
        null=True, blank=True,
        verbose_name="Protocol")
    application_profile = models.TextField(
        null=True, blank=True,
        verbose_name="ApplicationProfile")
    name = models.TextField(
        null=True, blank=True,
        verbose_name="Name")
    description = models.TextField(
        null=True, blank=True,
        verbose_name="Description")
    function = models.ManyToManyField(
        CIOnlineFunctionTerm,
        null=True, blank=True,
        verbose_name="Function")


class CIContact(models.Model):
    """
    Information required to enable contact with the responsible person or organization.
    Use obligation from referencing.
    """
    phone = models.OneToOneField(
        CITelephone, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Phone")
    address = models.OneToOneField(
        CIAddress, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Address")
    online_resource = models.OneToOneField(
        CIOnlineResource, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="OnlineResource")
    hours_of_service = models.TextField(
        null=True, blank=True,
        verbose_name="HoursOfService")
    contact_instruction = models.TextField(
        null=True, blank=True,
        verbose_name="ContactInstruction")


class CIResponsibleParty(models.Model):
    """
    Identification in terms of communication with
    the person(s) and organization(s) related to data.
    """
    individual_name = models.TextField(
        null=True, blank=True,
        verbose_name="IndividualName")
    organisation_name = models.TextField(
        null=True, blank=True,
        verbose_name="OrganisationName")
    position_name = models.TextField(
        null=True, blank=True,
        verbose_name="PositionName")
    contact_info = models.OneToOneField(
        CIContact, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="ContactInfo")
    role = models.ManyToManyField(
        CIRoleTerm, null=True, blank=True,
        verbose_name="Role")

    def __str__(self):
        return self.individual_name
