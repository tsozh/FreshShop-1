from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from .models import Goods, GoodsCategory, Banner, HotSearchWord
from .serializers import GoodsSerializer, CategorySerializer, BannerSerializer, IndexCategorySerializer, HotSearchWordSerializer
from .filters import GoodsFilter


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100


class GoodsViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    并且实现过滤、搜索和排序
    """
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_class = GoodsFilter
    search_fields = ['name', 'goods_brief', 'goods_desc']
    ordering_fields = ['market_price', 'shop_price']
    ordering = ('-goods_num', )
    pagination_class = StandardResultsSetPagination
    throttle_classes = (UserRateThrottle, AnonRateThrottle)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.click_num += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CategoryViewSet(CacheResponseMixin, viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = CategorySerializer
    filter_backends = (filters.OrderingFilter, DjangoFilterBackend)
    filter_fields = ['category_type']
    ordering_fields = ['add_time']
    ordering = ('id', )


class BannerViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = BannerSerializer
    queryset = Banner.objects.order_by('index')


class IndexCategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = IndexCategorySerializer
    queryset = GoodsCategory.objects.filter(is_tab=True, name__in=['酒水饮料', '粮油副食'])


class HotSearchWordViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = HotSearchWordSerializer
    queryset = HotSearchWord.objects.all()
