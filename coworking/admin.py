from django.contrib import admin
from .models import (
    Coworking, WorkplaceType, Workplace, Booking, BookingStatus,
    Payment, PaymentStatus, CoworkingImage, WorkplaceImage, Review, UserFavorite
)
from django.contrib.auth import get_user_model
from import_export.admin import ImportExportModelAdmin

User = get_user_model()

# INLINES
# Inline — это способ показать в админке связанные объекты внутри страницы основного объекта.
class CoworkingImageInline(admin.TabularInline):
    model = CoworkingImage
    extra = 1
    readonly_fields = ('created_at',)
    verbose_name = "Изображение коворкинга"
    verbose_name_plural = "Изображения коворкинга"

class WorkplaceImageInline(admin.TabularInline):
    model = WorkplaceImage
    extra = 1
    readonly_fields = ('created_at',)
    verbose_name = "Изображение рабочего места"
    verbose_name_plural = "Изображения рабочего места"

class UserFavoriteInline(admin.TabularInline):
    model = UserFavorite
    extra = 0
    raw_id_fields = ('user', 'workplace')
    verbose_name = "Избранное"
    verbose_name_plural = "Избранные рабочие места"

# ADMIN MODELS

@admin.register(Coworking)
class CoworkingAdmin(ImportExportModelAdmin):  # вместо admin.ModelAdmin
    list_display = ('name', 'address', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'address')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CoworkingImageInline]  # чтобы показывались изображения
    list_display_links = ('name',)    # чтобы имя было кликабельным

@admin.register(WorkplaceType)
class WorkplaceTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Workplace)
class WorkplaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'coworking', 'workplace_type', 'price_per_hour', 'is_active', 'created_at')
    list_filter = ('coworking', 'workplace_type', 'is_active')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [WorkplaceImageInline]
    raw_id_fields = ('coworking', 'workplace_type')

@admin.register(BookingStatus)
class BookingStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    # колонки в списке объектов
    list_display = (
        'user',
        'workplace',
        'start_time',
        'end_time',
        'duration_hours',
        'status',
        'created_at',
    )

    list_filter = ('status',)
    # включает строку поиска - реализован поиск по имени и рабочему месту
    search_fields = ('user__username', 'workplace__name')
    readonly_fields = ('created_at', 'updated_at')
    # для foreign keys - выбор через поиск
    raw_id_fields = ('user', 'workplace')
    # фильтрация по дате создания сверху страницы
    date_hierarchy = 'created_at'
    #позволяет вывести вычиляемое свойство в таблице
    @admin.display(description='Длительность (ч)')
    def duration_hours(self, obj):
        return round(
            (obj.end_time - obj.start_time).total_seconds() / 3600,
            2
        )


@admin.register(PaymentStatus)
class PaymentStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'payment_method', 'payment_date', 'status')
    list_filter = ('payment_date', 'status')
    search_fields = ('booking__user__username',)
    raw_id_fields = ('booking',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'coworking', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'coworking__name', 'comment')
    readonly_fields = ('created_at',)

@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'workplace', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'workplace__name')
    raw_id_fields = ('user', 'workplace')
    readonly_fields = ('added_at',)
