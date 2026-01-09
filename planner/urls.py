from django.urls import path
from . import views
from .views import (
    PlanTripView,
    DashboardView,
    DestinationSearchView,
    SelectHotelView,
    SelectHotelWithMapView,
    FilterHotelsView,
    SaveHotelView,
    SelectTransportCategoryView,
    SelectTransportView,
    SaveTransportView,
    SelectSeatsView,
    GetRealHotelsView,
    SearchRealHotelsView,
    BookRealHotelView,
    ClearTripDataView,
    PlanSelectionView,
    SelectPlanView,
    ItineraryDetailView,
    AddActivityView,
    RemoveActivityView,
    DownloadItineraryPDFView,
    TestWeatherAPIView,
    test_view,
)

app_name = 'planner'

urlpatterns = [
    path('', views.PlanTripView.as_view(), name='plan'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('search-destinations/', views.DestinationSearchView.as_view(), name='search_destinations'),
    path('select-hotel/<int:trip_id>/', views.SelectHotelView.as_view(), name='select_hotel'),
    path('select-hotel-map/<int:trip_id>/', views.SelectHotelWithMapView.as_view(), name='select_hotel_map'),
    path('filter-hotels/<int:destination_id>/', views.FilterHotelsView.as_view(), name='filter_hotels'),
    path('save-hotel/<int:trip_id>/', views.SaveHotelView.as_view(), name='save_hotel'),
    path('select-transport-category/<int:trip_id>/', views.SelectTransportCategoryView.as_view(), name='select_transport_category'),
    path('select-transport/<int:trip_id>/', views.SelectTransportView.as_view(), name='select_transport'),
    path('save-transport/<int:trip_id>/', views.SaveTransportView.as_view(), name='save_transport'),
    path('select-seats/<int:trip_id>/<int:transport_id>/', views.SelectSeatsView.as_view(), name='select_seats'),
    path('get-real-hotels/', views.GetRealHotelsView.as_view(), name='get_real_hotels'),
    path('search-real-hotels/<int:destination_id>/', views.SearchRealHotelsView.as_view(), name='search_real_hotels'),
    path('book-real-hotel/<int:trip_id>/', views.BookRealHotelView.as_view(), name='book_real_hotel'),
    path('clear-trip/', views.ClearTripDataView.as_view(), name='clear_trip'),
    path('test/', views.test_view, name='test'),
    
    # Plan selection and itinerary URLs
    path('trip/<int:trip_id>/plans/', views.PlanSelectionView.as_view(), name='plan_selection'),
    path('trip/<int:trip_id>/select-plan/', views.SelectPlanView.as_view(), name='select_plan'),
    path('trip/<int:trip_id>/itinerary/<str:plan_id>/', views.ItineraryDetailView.as_view(), name='itinerary_detail'),
    path('trip/<int:trip_id>/plan/<str:plan_id>/add-activity/', views.AddActivityView.as_view(), name='add_activity'),
    path('trip/<int:trip_id>/plan/<str:plan_id>/remove-activity/', views.RemoveActivityView.as_view(), name='remove_activity'),
    path('trip/<int:trip_id>/plan/<str:plan_id>/download-pdf/', views.DownloadItineraryPDFView.as_view(), name='download_itinerary_pdf'),
    
    # Weather testing URL - FIXED: Only TestWeatherAPIView exists
    path('test-weather/', TestWeatherAPIView.as_view(), name='test_weather'),
]