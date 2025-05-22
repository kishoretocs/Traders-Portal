from django_filters import rest_framework as filters
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Company, Watchlist
from .serializers import CompanySerializer, WatchlistSerializer
from rest_framework.exceptions import NotFound, ValidationError,APIException
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
import logging
from .throttles import WatchlistThrottle

logger = logging.getLogger(__name__)
  

class CompanyFilter(filters.FilterSet):
    symbol    = filters.CharFilter(field_name='symbol', lookup_expr='istartswith')
    company_name = filters.CharFilter(field_name='company_name', lookup_expr='icontains')

    class Meta:
        model = Company
        fields = ['symbol', 'company_name']

class CompanyListView(generics.ListAPIView):
    throttle_classes = [WatchlistThrottle]
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.AllowAny]
    filterset_class = CompanyFilter
    filter_backends = [DjangoFilterBackend, SearchFilter]  
    search_fields = ['company_name', 'symbol', 'scripcode']  
    def get_queryset(self):
        try:
            return Company.objects.all()
        except Exception as e:
            logger.error(f"Error while fetching companies: {e}")
            raise APIException("Unable to fetch companies at the moment.")
            

class WatchlistView(generics.ListAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            return Watchlist.objects.select_related('company').filter(user=self.request.user)
        except Exception as e:
            logger.error(f"Error fetching watchlist for user {self.request.user}: {e}")
            raise APIException("Unable to fetch watchlist at the moment.")

class AddToWatchlist(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            company_id = request.data.get("company_id")
            if not company_id:
                raise ValidationError("Missing 'company_id' in request data.")

            company = Company.objects.get(id=company_id)
            watch, created = Watchlist.objects.get_or_create(user=request.user, company=company)

            return Response(
                {"message": "Added to watchlist" if created else "Already exists"},
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
        except Company.DoesNotExist:
            logger.warning(f"Company ID {company_id} not found for user {request.user}")
            raise NotFound("Company not found.")
        except Exception as e:
            logger.error(f"Unexpected error in AddToWatchlist: {str(e)}")
            return Response({"error": "Something went wrong."}, status=500)

class RemoveFromWatchlist(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, company_id):
        try:
            watch = Watchlist.objects.filter(user=request.user, company_id=company_id)
            if not watch.exists():
                raise NotFound("Company not in your watchlist.")
            watch.delete()
            return Response({"message": "Removed from watchlist"}, status=200)
        except Exception as e:
            logger.error(f"Error removing watchlist item: {e}")
            return Response({"error": "Failed to remove."}, status=500)

