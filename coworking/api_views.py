from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Coworking, Workplace
from .serializers import CoworkingSerializer, WorkplaceSerializer
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend


# ================== PAGINATION ==================
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50

# ================== VIEWSETS ==================
class CoworkingViewSet(viewsets.ModelViewSet):
    queryset = Coworking.objects.all()
    serializer_class = CoworkingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'address', 'description']

    # Дополнительный метод GET для коворкингов с названием "Центр"
    @action(methods=['get'], detail=False)
    def centers(self, request):
        queryset = self.get_queryset().filter(name__icontains="Центр")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class WorkplaceViewSet(viewsets.ModelViewSet):
    queryset = Workplace.objects.all()
    serializer_class = WorkplaceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['coworking', 'is_active']
    search_fields = ['name']

    # Q-запрос: рабочие места активные или цена < 500
    @action(methods=['get'], detail=False)
    def active_or_cheap(self, request):
        queryset = self.get_queryset().filter(Q(is_active=True) | Q(price_per_hour__lt=500))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def smart_filter(self, request):
        queryset = self.get_queryset().filter(
            Q(is_active=True) &
            Q(price_per_hour__lt=1000) &
            ~Q(name__icontains='vip')
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=True)
    def deactivate(self, request, pk=None):
        workplace = self.get_object()
        workplace.is_active = False
        workplace.save()
        return Response({'status': 'Рабочее место деактивировано'})
