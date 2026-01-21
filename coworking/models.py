from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

# Пользователь и роли реализованы с помощью встроенных механизмов Django, поэтому отдельные модели не создавались, чтобы избежать дублирования.

class Coworking(models.Model):
    name = models.CharField('Название', max_length=255)
    address = models.CharField('Адрес', max_length=255)
    description = models.TextField('Описание')

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата изменения', auto_now=True)

    class Meta:
        # verbose_name чтобы интерфейс был понятен не разработчику, а администратору
        verbose_name = 'Коворкинг'
        verbose_name_plural = 'Коворкинги'

    # str определяет, как объект отображается в админке и в связях
    def __str__(self):
        return self.name

    history = HistoricalRecords()


class WorkplaceType(models.Model):
    name = models.CharField('Тип рабочего места', max_length=100)

    class Meta:
        verbose_name = 'Тип рабочего места'
        verbose_name_plural = 'Типы рабочих мест'

    def __str__(self):
        return self.name


class Workplace(models.Model):
    name = models.CharField('Название', max_length=255)
    coworking = models.ForeignKey(
        Coworking,
        on_delete=models.CASCADE,
        related_name='workplaces',
        verbose_name='Коворкинг'
    )
    workplace_type = models.ForeignKey(
        WorkplaceType,
        on_delete=models.PROTECT,
        verbose_name='Тип рабочего места'
    )
    price_per_hour = models.DecimalField(
        'Цена за час',
        max_digits=8,
        decimal_places=2
    )
    is_active = models.BooleanField('Активно', default=True)

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата изменения', auto_now=True)

    class Meta:
        verbose_name = 'Рабочее место'
        verbose_name_plural = 'Рабочие места'

    def __str__(self):
        return f'{self.name} ({self.coworking.name})'

    history = HistoricalRecords()


class BookingStatus(models.Model):
    name = models.CharField('Статус бронирования', max_length=100)

    class Meta:
        verbose_name = 'Статус бронирования'
        verbose_name_plural = 'Статусы бронирования'

    def __str__(self):
        return self.name


class Booking(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    workplace = models.ForeignKey(
        Workplace,
        on_delete=models.CASCADE,
        verbose_name='Рабочее место'
    )
    total_price = models.DecimalField(
        'Стоимость бронирования',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    start_time = models.DateTimeField('Время начала')
    end_time = models.DateTimeField('Время окончания')
    status = models.ForeignKey(
        BookingStatus,
        on_delete=models.PROTECT,
        verbose_name='Статус'
    )

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата изменения', auto_now=True)

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'

    def __str__(self):
        return f'Бронь #{self.id} — {self.workplace}'


class PaymentStatus(models.Model):
    name = models.CharField('Статус платежа', max_length=100)

    class Meta:
        verbose_name = 'Статус платежа'
        verbose_name_plural = 'Статусы платежей'

    def __str__(self):
        return self.name


class Payment(models.Model):
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        verbose_name='Бронирование'
    )
    amount = models.DecimalField(
        'Сумма',
        max_digits=10,
        decimal_places=2
    )
    payment_method = models.CharField(
        'Способ оплаты',
        max_length=100
    )
    payment_date = models.DateTimeField(
        'Дата оплаты'
    )
    status = models.ForeignKey(
        PaymentStatus,
        on_delete=models.PROTECT,
        verbose_name='Статус платежа'
    )

    class Meta:
        verbose_name = 'Оплата'
        verbose_name_plural = 'Оплаты'

    def __str__(self):
        return f'Оплата #{self.id}'


class CoworkingImage(models.Model):
    coworking = models.ForeignKey(
        Coworking,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to='coworkings/',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.coworking.name}"


class WorkplaceImage(models.Model):
    workplace = models.ForeignKey(
        Workplace,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to='workplaces/',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.workplace.name}"


class Review(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    coworking = models.ForeignKey(
        Coworking,
        on_delete=models.CASCADE,
        verbose_name='Коворкинг'
    )
    rating = models.PositiveSmallIntegerField('Оценка')
    comment = models.TextField('Комментарий')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'Отзыв от {self.user.username}'


class UserFavorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    workplace = models.ForeignKey(
        Workplace,
        on_delete=models.CASCADE,
        verbose_name='Рабочее место'
    )
    added_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Избранное рабочее место'
        verbose_name_plural = 'Избранные рабочие места'
        unique_together = ('user', 'workplace')

    def __str__(self):
        return f'{self.user.username} — {self.workplace.name}'
