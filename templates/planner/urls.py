from django.urls import path
from . import views
from .views import GetRealHotelsView, BookRealHotelView
from .views import (
    PlanTripView,
    DashboardView,
    DestinationSearchView,
    SelectHotelView,
    SelectHotelWithMapView,
    FilterHotelsView,
    SaveHotelView,
    DestinationDetailView,
    ConfirmSeatBookingView, 
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
    ConfirmBookingView,
    TripListView,
    UpcomingTripsView,
    TripCostAnalysisView,
    VisitedDestinationsView,
    DestinationListView, 
    DestinationAutocompleteView,
    # ADD THESE TWO NEW VIEWS:
    RegionPlacesView,
    PlaceDetailView,
)

app_name = 'planner'

urlpatterns = [
    # Main dashboard and planning
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('plan/', views.PlanTripView.as_view(), name='plan'),
    
    # Destinations browsing
    path('destinations/', DestinationListView.as_view(), name='destinations'),
    path('destinations/<int:destination_id>/', DestinationDetailView.as_view(), name='destination_detail'),
    path('destinations-autocomplete/', DestinationAutocompleteView.as_view(), name='destinations_autocomplete'),
    
    # NEW: Region and Place URLs (ADD THESE)
    path('region/<int:region_id>/places/', RegionPlacesView.as_view(), name='region_places'),
    path('place/<int:place_id>/', PlaceDetailView.as_view(), name='place_detail'),
    
    # Hotel selection
    path('plan/<int:trip_id>/hotels/', views.SelectHotelView.as_view(), name='select_hotel'),
    path('select-hotel/<int:trip_id>/', views.SelectHotelView.as_view(), name='select_hotel_alt'),
    path('select-hotel-map/<int:trip_id>/', views.SelectHotelWithMapView.as_view(), name='select_hotel_map'),
    path('filter-hotels/<int:destination_id>/', views.FilterHotelsView.as_view(), name='filter_hotels'),
    path('plan/<int:trip_id>/hotels/select/', views.SaveHotelView.as_view(), name='save_hotel'),
    
    # Transport selection
    path('plan/<int:trip_id>/transport/', views.SelectTransportCategoryView.as_view(), name='select_transport_category'),
    path('plan/<int:trip_id>/transport/list/', views.SelectTransportView.as_view(), name='select_transport'),
    path('plan/<int:trip_id>/transport/save/', views.SaveTransportView.as_view(), name='save_transport'),
    path('select-seats/<int:trip_id>/<int:transport_id>/', views.SelectSeatsView.as_view(), name='select_seats'),
    
    # Plan selection and itinerary
    path('trip/<int:trip_id>/plans/', views.PlanSelectionView.as_view(), name='plan_selection'),
    path('trip/<int:trip_id>/select-plan/', views.SelectPlanView.as_view(), name='select_plan'),
    path('trip/<int:trip_id>/itinerary/<str:plan_id>/', views.ItineraryDetailView.as_view(), name='itinerary_detail'),
    path('trip/<int:trip_id>/plan/<str:plan_id>/download-pdf/', views.DownloadItineraryPDFView.as_view(), name='download_itinerary_pdf'),
    
    # Trip confirmation
    path('trip/<int:trip_id>/confirm-booking/', views.ConfirmBookingView.as_view(), name='confirm_booking'),
    path('trip/<int:trip_id>/confirm-seats/', views.ConfirmSeatBookingView.as_view(), name='confirm_seat_booking'),
    
    # Activities
    path('trip/<int:trip_id>/plan/<str:plan_id>/add-activity/', views.AddActivityView.as_view(), name='add_activity'),
    path('trip/<int:trip_id>/plan/<str:plan_id>/remove-activity/', views.RemoveActivityView.as_view(), name='remove_activity'),
    
    # Real hotels API
    path('get-real-hotels/', GetRealHotelsView.as_view(), name='get_real_hotels'),
    path('search-real-hotels/<int:destination_id>/', views.SearchRealHotelsView.as_view(), name='search_real_hotels'),
    path('trip/<int:trip_id>/book-real-hotel/', BookRealHotelView.as_view(), name='book_real_hotel'),
    
    # Search
    path('search-destinations/', views.DestinationSearchView.as_view(), name='search_destinations'),
    
    # Clear trip
    path('clear-trip/', views.ClearTripDataView.as_view(), name='clear_trip'),
    
    # Weather testing
    path('test-weather/', TestWeatherAPIView.as_view(), name='test_weather'),
    
    # Dashboard analytics
    path('dashboard/trips/', TripListView.as_view(), name='trip_list'),
    path('dashboard/trips/upcoming/', UpcomingTripsView.as_view(), name='upcoming_trips'),
    path('dashboard/cost-analysis/', TripCostAnalysisView.as_view(), name='trip_cost_analysis'),
    path('dashboard/visited-destinations/', VisitedDestinationsView.as_view(), name='visited_destinations'),
]