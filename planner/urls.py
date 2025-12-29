# C:\Users\ASUS\MyanmarTravelPlanner\planner\urls.py
from django.urls import path
from . import views

app_name = 'planner'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('plan/', views.PlanTripView.as_view(), name='plan'),
    path('clear-trip/', views.ClearTripDataView.as_view(), name='clear_trip'),  # Add this line
   # path('test/', views.test_view, name='test'),
    path('search-destinations/', views.DestinationSearchView.as_view(), name='search_destinations'),
    path('select-hotel/<int:trip_id>/', views.SelectHotelView.as_view(), name='select_hotel'),
    path('select-hotel-map/<int:trip_id>/', views.SelectHotelWithMapView.as_view(), name='select_hotel_map'),
    path('save-hotel/<int:trip_id>/', views.SaveHotelView.as_view(), name='save_hotel'),
    path('filter-hotels/<int:destination_id>/', views.FilterHotelsView.as_view(), name='filter_hotels'),
    path('get-real-hotels/', views.GetRealHotelsView.as_view(), name='get_real_hotels'),
    path('book-real-hotel/<int:trip_id>/', views.BookRealHotelView.as_view(), name='book_real_hotel'),
    path('select-transport/<int:trip_id>/', views.SelectTransportView.as_view(), name='select_transport'),
    path('select-transport-category/<int:trip_id>/', views.SelectTransportCategoryView.as_view(), name='select_transport_category'),
    path('select-seats/<int:trip_id>/<int:transport_id>/', views.SelectSeatsView.as_view(), name='select_seats'),
    path('save-transport/<int:trip_id>/', views.SaveTransportView.as_view(), name='save_transport'),
]