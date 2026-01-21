from django.shortcuts import render, get_object_or_404, redirect
from .models import Coworking, Workplace, CoworkingImage, WorkplaceImage
from .forms import CoworkingForm, WorkplaceForm, CoworkingImageForm, WorkplaceImageForm, BookingForm, Payment, PaymentStatus
from .models import Booking, BookingStatus
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime, timedelta, time
from django.utils import timezone
from decimal import Decimal
from .forms import PaymentForm
from django.contrib import messages
from .models import Coworking, Review
from .forms import ReviewForm
from .models import Workplace, UserFavorite

# Проверка, является ли пользователь админом
def is_admin(user):
    return user.is_staff

# -----------------------------
# Коворкинги
# -----------------------------

def coworking_list(request):
    coworkings = Coworking.objects.all()

    # Для каждого коворкинга выбираем первое изображение (или None)
    for coworking in coworkings:
        coworking.first_image = coworking.images.filter(image__isnull=False).first()

    return render(request, 'coworking/coworking_list.html', {
        'coworkings': coworkings
    })

def coworking_detail(request, pk):
    coworking = get_object_or_404(Coworking, pk=pk)

    workplaces = coworking.workplaces.all()

    reviews = Review.objects.filter(coworking=coworking).select_related('user').order_by('-created_at')

    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = request.user.userfavorite_set.values_list('workplace_id', flat=True)

    context = {
        'coworking': coworking,
        'workplaces': workplaces,
        'reviews': reviews,
        'user_favorites': user_favorites,
    }
    return render(request, 'coworking/coworking_detail.html', context)


@login_required
@user_passes_test(is_admin)
def coworking_create(request):
    if request.method == 'POST':
        form = CoworkingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('coworking:coworking_list')
    else:
        form = CoworkingForm()

    return render(request, 'coworking/coworking_form.html', {
        'form': form,
        'title': 'Добавить коворкинг'
    })

@login_required
@user_passes_test(is_admin)
def coworking_update(request, pk):
    coworking = get_object_or_404(Coworking, pk=pk)
    if request.method == 'POST':
        form = CoworkingForm(request.POST, instance=coworking)
        if form.is_valid():
            form.save()
            return redirect('coworking:coworking_detail', pk=pk)
    else:
        form = CoworkingForm(instance=coworking)

    return render(request, 'coworking/coworking_form.html', {
        'form': form,
        'title': 'Редактировать коворкинг'
    })

@login_required
@user_passes_test(is_admin)
def coworking_delete(request, pk):
    coworking = get_object_or_404(Coworking, pk=pk)
    if request.method == 'POST':
        coworking.delete()
        return redirect('coworking:coworking_list')

    return render(request, 'coworking/coworking_confirm_delete.html', {
        'coworking': coworking
    })

# -----------------------------
# Рабочие места
# -----------------------------

# Список рабочих мест для коворкинга (видно всем)
def workplace_list(request, coworking_id):
    coworking = get_object_or_404(Coworking, id=coworking_id)
    workplaces = coworking.workplaces.all()
    return render(request, 'coworking/workplace_list.html', {
        'coworking': coworking,
        'workplaces': workplaces
    })

# Детальная страница рабочего места
def workplace_detail(request, pk):
    workplace = get_object_or_404(Workplace, id=pk)

    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = request.user.userfavorite_set.values_list('workplace_id', flat=True)

    context = {
        'workplace': workplace,
        'user_favorites': user_favorites
    }
    return render(request, 'coworking/workplace_detail.html', context)


@login_required
@user_passes_test(is_admin)
def workplace_create(request, coworking_id):
    coworking = get_object_or_404(Coworking, id=coworking_id)

    if request.method == 'POST':
        form = WorkplaceForm(request.POST)
        if form.is_valid():
            workplace = form.save(commit=False)
            workplace.coworking = coworking
            workplace.save()
            return redirect('coworking:coworking_detail', pk=coworking.id)
    else:
        form = WorkplaceForm()

    return render(request, 'coworking/workplace_form.html', {
        'form': form,
        'title': f'Добавить рабочее место для {coworking.name}'
    })

# Редактирование рабочего места (только админ)
@login_required
@user_passes_test(is_admin)
def workplace_update(request, pk):
    workplace = get_object_or_404(Workplace, id=pk)
    if request.method == 'POST':
        form = WorkplaceForm(request.POST, instance=workplace)
        if form.is_valid():
            form.save()
            return redirect('coworking:workplace_detail', pk=workplace.id)
    else:
        form = WorkplaceForm(instance=workplace)
    return render(request, 'coworking/workplace_form.html', {
        'form': form,
        'title': f'Редактировать рабочее место {workplace.name}'
    })

# Удаление рабочего места (только админ)
@login_required
@user_passes_test(is_admin)
def workplace_delete(request, pk):
    workplace = get_object_or_404(Workplace, id=pk)
    if request.method == 'POST':
        coworking_id = workplace.coworking.id
        workplace.delete()
        return redirect('coworking:coworking_detail', pk=coworking_id)
    return render(request, 'coworking/workplace_confirm_delete.html', {'workplace': workplace})

# -----------------------------
# Загрузка изображений
# -----------------------------

@login_required
@user_passes_test(is_admin)
def coworking_image_add(request, coworking_id):
    coworking = get_object_or_404(Coworking, id=coworking_id)

    if request.method == 'POST':
        form = CoworkingImageForm(request.POST, request.FILES)
        if form.is_valid():
            coworking_image = form.save(commit=False)
            coworking_image.coworking = coworking
            coworking_image.save()
            return redirect('coworking:coworking_detail', pk=coworking.id)
    else:
        form = CoworkingImageForm()

    return render(request, 'coworking/coworking_image_form.html', {
        'form': form,
        'title': f'Добавить изображение для {coworking.name}',
        'coworking': coworking,  # <--- добавляем эту строку
    })

@login_required
@user_passes_test(is_admin)
def coworking_image_delete(request, pk):
    image = get_object_or_404(CoworkingImage, id=pk)
    coworking_id = image.coworking.id

    if request.method == 'POST':
        image.delete()
        return redirect('coworking:coworking_detail', pk=coworking_id)

    return render(request, 'coworking/coworking_image_confirm_delete.html', {'image': image})




@login_required
@user_passes_test(is_admin)
def workplace_image_add(request, workplace_id):
    workplace = get_object_or_404(Workplace, id=workplace_id)

    if request.method == 'POST':
        form = WorkplaceImageForm(request.POST, request.FILES)
        if form.is_valid():
            workplace_image = form.save(commit=False)
            workplace_image.workplace = workplace
            workplace_image.save()
            return redirect('coworking:workplace_detail', pk=workplace.id)
    else:
        form = WorkplaceImageForm()

    return render(request, 'coworking/workplace_image_form.html', {
        'form': form,
        'title': f'Добавить изображение для {workplace.name}',
        'workplace': workplace,  # <--- добавляем объект для ссылки в шаблоне
    })

@login_required
@user_passes_test(is_admin)
def workplace_image_delete(request, pk):
    image = get_object_or_404(WorkplaceImage, id=pk)
    workplace_id = image.workplace.id

    if request.method == 'POST':
        image.delete()
        return redirect('coworking:workplace_detail', pk=workplace_id)

    return render(request, 'coworking/workplace_image_confirm_delete.html', {'image': image})


# -----------------------------
# Бронирования
# -----------------------------

@login_required
def booking_create(request, workplace_id):
    workplace = get_object_or_404(Workplace, id=workplace_id, is_active=True)

    # Используем часовой пояс из настроек Django
    from django.conf import settings
    LOCAL_TZ = timezone.get_current_timezone()
    
    # Получаем все активные бронирования для этого места
    now_utc = timezone.now()
    
    existing_bookings = Booking.objects.filter(
        workplace=workplace,
        end_time__gte=now_utc - timedelta(hours=1)
    ).order_by('start_time')

    # Формируем busy_slots в локальном времени
    busy_slots = []
    for booking in existing_bookings:
        # Конвертируем время бронирования в локальный часовой пояс
        start_local = timezone.localtime(booking.start_time, LOCAL_TZ)
        end_local = timezone.localtime(booking.end_time, LOCAL_TZ)
        
        current = start_local
        while current < end_local:
            busy_slots.append({
                'date': current.date(),
                'hour': current.hour,
                'datetime': current
            })
            current += timedelta(hours=1)

    if request.method == 'POST':
        form = BookingForm(request.POST, workplace=workplace)
        if form.is_valid():
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']

            duration_hours = Decimal((end_time - start_time).total_seconds() / 3600)
            total_price = workplace.price_per_hour * duration_hours

            status, _ = BookingStatus.objects.get_or_create(name='Активно')

            Booking.objects.create(
                user=request.user,
                workplace=workplace,
                start_time=start_time,
                end_time=end_time,
                status=status,
                total_price=total_price
            )

            return redirect('coworking:booking_list')
    else:
        form = BookingForm(workplace=workplace)

    # Группируем занятые слоты по дням
    busy_by_date = {}
    for slot in busy_slots:
        date_str = slot['date'].strftime('%Y-%m-%d')
        if date_str not in busy_by_date:
            busy_by_date[date_str] = []
        busy_by_date[date_str].append(slot['hour'])

    for date_str in busy_by_date:
        busy_by_date[date_str].sort()

    return render(request, 'coworking/booking_form.html', {
        'workplace': workplace,
        'form': form,
        'busy_slots': busy_slots,
        'busy_by_date': busy_by_date,
        'current_time': timezone.localtime(timezone.now(), LOCAL_TZ).strftime('%Y-%m-%d %H:%M')  # Для отладки
    })

@login_required
def booking_list(request):
    # Показываем только бронирования текущего пользователя
    bookings = Booking.objects.filter(user=request.user).order_by('-start_time')
    return render(request, 'coworking/booking_list.html', {
        'bookings': bookings
    })

@login_required
def booking_update(request, pk):
    booking = get_object_or_404(Booking, id=pk, user=request.user)

    # Используем часовой пояс из настроек Django
    LOCAL_TZ = timezone.get_current_timezone()
    
    # Конвертируем время брони в локальный пояс для initial данных
    start_local = timezone.localtime(booking.start_time, LOCAL_TZ)
    end_local = timezone.localtime(booking.end_time, LOCAL_TZ)
    
    initial = {
        'date_start': start_local.date(),
        'date_end': end_local.date(),
        'start_hour': start_local.hour,
        'end_hour': end_local.hour,
    }

    # Получаем занятые слоты в локальном времени
    now_utc = timezone.now()
    existing_bookings = Booking.objects.filter(
        workplace=booking.workplace,
        end_time__gte=now_utc - timedelta(hours=1)
    ).exclude(id=booking.id).order_by('start_time')
    
    busy_slots = []
    for b in existing_bookings:
        b_start_local = timezone.localtime(b.start_time, LOCAL_TZ)
        b_end_local = timezone.localtime(b.end_time, LOCAL_TZ)
        current = b_start_local
        while current < b_end_local:
            busy_slots.append({
                'date': current.date(),
                'hour': current.hour,
            })
            current += timedelta(hours=1)
    
    # Группируем по дням
    busy_by_date = {}
    for slot in busy_slots:
        date_str = slot['date'].strftime('%Y-%m-%d')
        if date_str not in busy_by_date:
            busy_by_date[date_str] = []
        busy_by_date[date_str].append(slot['hour'])
    
    for date_str in busy_by_date:
        busy_by_date[date_str].sort()

    if request.method == 'POST':
        form = BookingForm(
            request.POST,
            workplace=booking.workplace,
            booking=booking
        )
        if form.is_valid():
            booking.start_time = form.cleaned_data['start_time']
            booking.end_time = form.cleaned_data['end_time']
            
            duration_hours = Decimal((booking.end_time - booking.start_time).total_seconds() / 3600)
            booking.total_price = booking.workplace.price_per_hour * duration_hours
            
            booking.save()
            return redirect('coworking:booking_list')
    else:
        form = BookingForm(
            initial=initial,
            workplace=booking.workplace,
            booking=booking
        )

    return render(request, 'coworking/booking_form.html', {
        'form': form,
        'workplace': booking.workplace,
        'booking': booking,
        'busy_by_date': busy_by_date
    })

@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, id=pk, user=request.user)

    if request.method == 'POST':
        booking.delete()
        return redirect('coworking:booking_list')

    return render(request, 'coworking/booking_confirm_cancel.html', {
        'booking': booking
    })

def booking_payment(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    
    if request.method == 'POST':
        # создаём оплату сразу
        Payment.objects.create(
            booking=booking,
            amount=booking.total_price,
            payment_method=request.POST.get('payment_method', 'условно'),
            payment_date=timezone.now(),  # <--- обязательно!
            status=PaymentStatus.objects.get(name='Оплачен')  # пример
        )
        return redirect('coworking:booking_list')

    return render(request, 'coworking/booking_payment.html', {'booking': booking})

@login_required
def review_create(request, coworking_id):
    coworking = get_object_or_404(Coworking, id=coworking_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.coworking = coworking
            review.save()
            return redirect('coworking:coworking_detail', pk=coworking.id)
    else:
        form = ReviewForm()

    return render(request, 'coworking/review_form.html', {
        'form': form,
        'coworking': coworking
    })

@login_required
def favorite_add(request, pk):
    workplace = get_object_or_404(Workplace, pk=pk)
    request.user.userfavorite_set.get_or_create(workplace=workplace)
    return redirect('coworking:workplace_detail', pk=pk)


@login_required
def favorite_remove(request, pk):
    workplace = get_object_or_404(Workplace, pk=pk)
    request.user.userfavorite_set.filter(workplace=workplace).delete()
    return redirect('coworking:workplace_detail', pk=pk)


@login_required
def favorite_list(request):
    # Получаем все избранные рабочие места пользователя
    favorites = Workplace.objects.filter(userfavorite__user=request.user)
    return render(request, 'coworking/favorite_list.html', {
        'favorites': favorites
    })