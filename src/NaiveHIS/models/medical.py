from django.db import models
from django.utils.translation import gettext_lazy as _


class Discipline(models.TextChoices):
    """Angelehnt an die Muster-Weiterbildungsordnung der BAK von 2018"""

    GENERAL_PRACTICE = ('general_practice', _('Allgemeinmedizin'))
    ANESTHESIA = ('anesthesia', _('Anästhesiologie'))
    ANATOMY = ('anatomy', _('Anatomie'))
    WORKPLACE_MED = ('occupational_medicine', _('Arbeitsmedizin'))
    OPHTALMOLOGY = ('opthalmology', _('Augenheilkunde'))
    BIOCHEMISTRY = ('biochemistry', _('Biochemie'))
    SURGERY = ('surgery', _('Chirurgie'))
    GYNECOLOGY = ('gynecology', _('Frauenheilkunde und Geburtshilfe'))
    ENT = ('ent', _('Hals-/Nasen-/Ohrenheilkunde'))
    DERMATOLOGY = ('dermatology', _('Haut- und Geschlechtskrankheiten'))
    HUMAN_GENETICS = ('human_genetics', _('Humangenetik'))
    HYG_ENV_MED = ('hygiene_and_environmental_medicine', _('Hygiene- und Umweltmedizin'))
    INNER_MED = ('inner_medicine', _('Innere Medizin'))
    PAEDIATRY = ('paediatry', _('Kinder- und Jugendmedizin'))
    PAEDIATRIC_PSYCHIATRY = ('paediatric_psychiatry_and_psychotherapy', _('Kinder- und Jugendpsychiatrie und -psychotherapie'))
    LAB_MED = ('laboratory_medicine', _('Laboratoriumsmedizin'))
    MICROBIOLOGY = ('microbiology_virology_and_infection_epidemology', _('Mikrobiologie, Virologie und Infektionsepidemiologie'))
    MAXILLOFACIAL_SURGERY = ('maxillofacial_surgery', _('Mund-/Kiefer-/Gesichtschirurgie'))
    NEURO_SURGERY = ('neuro_surgery', _('Neurochirurgie'))
    NEUROLOGY = ('neurology', _('Neurologie'))
    NUCLEAR_MED = ('nuclear_medicine', _('Nuklearmedizin'))
    PUBLIC_HEALTH_SYSTEM = ('public_health_system', _('Öffentliches Gesundheitswesen'))
    PATHOLOGY = ('pathology', _('Pathologie'))
    PHARMACOLOGY = ('pharmacology', _('Pharmakologie'))
    PHONIATRICS = ('phoniatrics_and_paediatric_audiology', _('Phoniatrie und Pädaudiologie'))
    PHYSICAL_MED = ('physical_medicine_and_rehabilitation', _('Physikalische und rehabilitative Medizin'))
    PHYSIOLOGY = ('physiology', _('Physiologie'))
    PSYCHIATRY = ('psychiatry_and_psychotherapy', _('Psychiatrie und Psychotherapie'))
    PSYCHOSOMATIC_MED = ('psychosomatic_medicine_and_psychotherapy', _('Psychosomatische Medizin und Psychotherapie'))
    RADIOLOGY = ('radiology', _('Radiologie'))
    FORENSIC_MED = ('forensic_medicine', _('Rechtsmedizin'))
    RADIOTHERAPY = ('radiotherapy', _('Strahlentherapie'))
    TRANSFUSION_MED = ('transfusion_medicine', _('Transfusionsmedizin'))
    UROLOGY = ('urology', _('Urologie'))

    def __str__(self):
        return self.label()
