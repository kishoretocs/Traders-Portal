from django.urls import path
from .views import (
    CompanyListView,
    WatchlistView,
    AddToWatchlist,
    RemoveFromWatchlist
)

urlpatterns = [
    path('companies/', CompanyListView.as_view(), name='company-list'),
    path('watchlist/', WatchlistView.as_view(), name='watchlist'),
    path('watchlist/add/', AddToWatchlist.as_view(), name='watchlist-add'),
    path('watchlist/remove/<int:company_id>/', RemoveFromWatchlist.as_view(), name='watchlist-remove'),
]
