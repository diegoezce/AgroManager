"""
Django forms for animal management with comprehensive validation.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .models import Animal, Breed, PastureZone, WeightRecord, HealthRecord


class AnimalForm(forms.ModelForm):
    """Form for creating and editing animals with field-level validation."""

    class Meta:
        model = Animal
        fields = [
            'identifier', 'species', 'breed', 'birth_date',
            'birth_weight', 'health_status', 'pasture_zone', 'is_for_sale'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'identifier': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., AGR-001',
                'maxlength': '50',
            }),
            'species': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Bovino, Equino',
            }),
            'breed': forms.Select(attrs={'class': 'form-control'}),
            'birth_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Weight in kg',
            }),
            'health_status': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Healthy, Sick',
            }),
            'pasture_zone': forms.Select(attrs={'class': 'form-control'}),
            'is_for_sale': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_identifier(self):
        identifier = self.cleaned_data.get('identifier', '').strip()

        if not identifier:
            raise ValidationError("Identifier cannot be empty")

        if len(identifier) < 2:
            raise ValidationError("Identifier must be at least 2 characters long")

        if len(identifier) > 50:
            raise ValidationError("Identifier cannot exceed 50 characters")

        # Check for uniqueness (except when editing)
        qs = Animal.objects.filter(identifier=identifier)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError(f"An animal with identifier '{identifier}' already exists")

        return identifier

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')

        if not birth_date:
            raise ValidationError("Birth date is required")

        today = timezone.now().date()
        if birth_date > today:
            raise ValidationError("Birth date cannot be in the future")

        # Check if date is reasonable (not more than 30 years ago)
        min_date = today - timedelta(days=365 * 30)
        if birth_date < min_date:
            raise ValidationError("Birth date seems too far in the past (>30 years)")

        return birth_date

    def clean_birth_weight(self):
        weight = self.cleaned_data.get('birth_weight')

        if weight is None:
            raise ValidationError("Birth weight is required")

        if weight < 0:
            raise ValidationError("Weight cannot be negative")

        if weight < 5:
            raise ValidationError("Birth weight seems too low (<5kg)")

        if weight > 150:
            raise ValidationError("Birth weight seems too high (>150kg)")

        return weight

    def clean_species(self):
        species = self.cleaned_data.get('species', '').strip()

        if not species:
            raise ValidationError("Species is required")

        return species

    def clean_health_status(self):
        health_status = self.cleaned_data.get('health_status', '').strip()

        if not health_status:
            raise ValidationError("Health status is required")

        return health_status


class BreedForm(forms.ModelForm):
    """Form for creating and editing cattle breeds."""

    class Meta:
        model = Breed
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Hereford',
                'maxlength': '100',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Breed characteristics and information',
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()

        if not name:
            raise ValidationError("Breed name cannot be empty")

        if len(name) < 2:
            raise ValidationError("Breed name must be at least 2 characters")

        # Check for uniqueness
        qs = Breed.objects.filter(name=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError(f"Breed '{name}' already exists")

        return name


class WeightRecordForm(forms.ModelForm):
    """Form for recording animal weights."""

    class Meta:
        model = WeightRecord
        fields = ['weight', 'date_recorded']
        widgets = {
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Weight in kg',
            }),
            'date_recorded': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
        }

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')

        if weight is None:
            raise ValidationError("Weight is required")

        if weight < 0:
            raise ValidationError("Weight cannot be negative")

        if weight > 2000:
            raise ValidationError("Weight seems unusually high (>2000kg)")

        return weight

    def clean_date_recorded(self):
        date_recorded = self.cleaned_data.get('date_recorded')

        if not date_recorded:
            raise ValidationError("Recording date is required")

        if date_recorded > timezone.now().date():
            raise ValidationError("Recording date cannot be in the future")

        return date_recorded


class PastureZoneForm(forms.ModelForm):
    """Form for creating and editing pasture zones."""

    class Meta:
        model = PastureZone
        fields = ['name', 'area_size', 'grazing_capacity', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., North Field',
                'maxlength': '100',
            }),
            'area_size': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Area in hectares',
            }),
            'grazing_capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Maximum animals',
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()

        if not name:
            raise ValidationError("Zone name cannot be empty")

        return name

    def clean_area_size(self):
        area_size = self.cleaned_data.get('area_size')

        if area_size is not None and area_size < 0:
            raise ValidationError("Area size cannot be negative")

        return area_size

    def clean_grazing_capacity(self):
        capacity = self.cleaned_data.get('grazing_capacity')

        if capacity is not None and capacity < 0:
            raise ValidationError("Grazing capacity cannot be negative")

        return capacity


class HealthRecordForm(forms.ModelForm):
    """Form for recording animal health checkups."""

    class Meta:
        model = HealthRecord
        fields = ['checkup_date', 'health_status', 'medication_given', 'notes']
        widgets = {
            'checkup_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'health_status': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Healthy, Sick, Recovering',
            }),
            'medication_given': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Medications applied (optional)',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes (optional)',
            }),
        }

    def clean_checkup_date(self):
        date = self.cleaned_data.get('checkup_date')

        if not date:
            raise ValidationError("Checkup date is required")

        if date > timezone.now().date():
            raise ValidationError("Checkup date cannot be in the future")

        return date

    def clean_health_status(self):
        status = self.cleaned_data.get('health_status', '').strip()

        if not status:
            raise ValidationError("Health status is required")

        return status


class BulkAnimalImportForm(forms.Form):
    """Form for bulk importing animals from CSV file."""

    file = forms.FileField(
        label='CSV File',
        help_text='Upload a CSV file with columns: identifier, species, breed, birth_date (YYYY-MM-DD), birth_weight, health_status',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv',
        })
    )

    def clean_file(self):
        file = self.cleaned_data.get('file')

        if not file:
            raise ValidationError("Please select a file")

        if not file.name.endswith('.csv'):
            raise ValidationError("File must be in CSV format (.csv)")

        # Check file size (5MB max)
        if file.size > 5 * 1024 * 1024:
            raise ValidationError("File size cannot exceed 5MB")

        return file
