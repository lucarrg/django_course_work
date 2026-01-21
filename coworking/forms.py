from django import forms
from .models import (
    Coworking,
    Workplace,
    CoworkingImage,
    WorkplaceImage,
    Booking,
    BookingStatus,
    Review
)
from .models import Payment, PaymentStatus
from django.utils import timezone
from datetime import datetime, time, timedelta

class CoworkingForm(forms.ModelForm):
    class Meta:
        model = Coworking
        fields = ['name', 'address', 'description']


class WorkplaceForm(forms.ModelForm):
    class Meta:
        model = Workplace
        fields = ['name', 'coworking', 'workplace_type', 'price_per_hour', 'is_active']


# -----------------------------
# Формы загрузки изображений
# -----------------------------

class CoworkingImageForm(forms.ModelForm):
    class Meta:
        model = CoworkingImage
        fields = ['image']


class WorkplaceImageForm(forms.ModelForm):
    class Meta:
        model = WorkplaceImage
        fields = ['image']


HOUR_CHOICES = [(h, f"{h}:00") for h in range(0, 24)]


class BookingForm(forms.Form):
    date_start = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Дата начала'
    )
    date_end = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Дата окончания'
    )
    start_hour = forms.ChoiceField(
        choices=HOUR_CHOICES,
        label='Час начала'
    )
    end_hour = forms.ChoiceField(
        choices=HOUR_CHOICES,
        label='Час окончания'
    )

    def __init__(self, *args, workplace=None, booking=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.workplace = workplace
        self.booking = booking

    def clean(self):
        cleaned = super().clean()

        date_start = cleaned.get('date_start')
        date_end = cleaned.get('date_end')
        start_hour = cleaned.get('start_hour')
        end_hour = cleaned.get('end_hour')

        if not all([date_start, date_end, start_hour, end_hour]):
            return cleaned

        # Преобразуем часы в int
        start_hour = int(start_hour)
        end_hour = int(end_hour)

        # Формируем aware datetime
        start_dt = timezone.make_aware(datetime.combine(date_start, datetime.min.time()) + timedelta(hours=start_hour))
        end_dt = timezone.make_aware(datetime.combine(date_end, datetime.min.time()) + timedelta(hours=end_hour))

        now = timezone.now()
        if start_dt < now:
            raise forms.ValidationError('Нельзя бронировать в прошлом.')
        if start_dt >= end_dt:
            raise forms.ValidationError('Время окончания должно быть позже времени начала.')

        # Проверка пересечений
        conflicts = Booking.objects.filter(
            workplace=self.workplace,
            start_time__lt=end_dt,
            end_time__gt=start_dt
        )
        if self.booking:
            conflicts = conflicts.exclude(id=self.booking.id)
        if conflicts.exists():
            raise forms.ValidationError('Рабочее место уже забронировано на выбранное время.')

        cleaned['start_time'] = start_dt
        cleaned['end_time'] = end_dt
        return cleaned

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method']
        widgets = {
            'payment_method': forms.TextInput(attrs={'placeholder': 'Например, карта, наличные'}),
        }

    def __init__(self, *args, booking=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.booking = booking

    def save(self, commit=True):
        payment = super().save(commit=False)
        payment.booking = self.booking
        payment.amount = self.booking.total_price
        # По умолчанию статус "частично/не оплачен"
        payment.status, _ = PaymentStatus.objects.get_or_create(name='не оплачен')
        if commit:
            payment.save()
        return payment

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        labels = {
            'rating': 'Оценка (1–5)',
            'comment': 'Комментарий',
        }
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }