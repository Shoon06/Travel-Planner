from django.urls import path
from . import views
from users.views import admin_how_it_works as how_it_works
from .views import (
    PlanTripView,
    DashboardView,
    RegionPlacesView,
    PlaceDetailView,
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
    ConfirmBookingView,  # ADD THIS IMPORT
    TripListView,
    UpcomingTripsView,
    TripCostAnalysisView,
    VisitedDestinationsView,
    DestinationListView, 
    DestinationAutocompleteView,
)

app_name = 'planner'

urlpatterns = [
    # Main trip planning
    path('', views.PlanTripView.as_view(), name='plan'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Plan selection
    path('trip/<int:trip_id>/plans/', views.PlanSelectionView.as_view(), name='plan_selection'),
    path('trip/<int:trip_id>/select-plan/', views.SelectPlanView.as_view(), name='select_plan'),
    path('how-it-works/', how_it_works, name='how_it_works'),
    # Trip confirmation - FIXED: Only one endpoint for confirming entire trip
    path('trip/<int:trip_id>/confirm-booking/', views.ConfirmBookingView.as_view(), name='confirm_booking'),
    
    # Seat confirmation (separate from trip confirmation)
    path('trip/<int:trip_id>/confirm-seats/', views.ConfirmSeatBookingView.as_view(), name='confirm_seat_booking'),
    
    # Hotel selection
    path('select-hotel/<int:trip_id>/', views.SelectHotelView.as_view(), name='select_hotel'),
    path('select-hotel-map/<int:trip_id>/', views.SelectHotelWithMapView.as_view(), name='select_hotel_map'),
    path('filter-hotels/<int:destination_id>/', views.FilterHotelsView.as_view(), name='filter_hotels'),
    path('save-hotel/<int:trip_id>/', views.SaveHotelView.as_view(), name='save_hotel'),
    
    # Transport selection
    path('select-transport-category/<int:trip_id>/', views.SelectTransportCategoryView.as_view(), name='select_transport_category'),
    path('select-transport/<int:trip_id>/', views.SelectTransportView.as_view(), name='select_transport'),
    path('save-transport/<int:trip_id>/', views.SaveTransportView.as_view(), name='save_transport'),
    path('select-seats/<int:trip_id>/<int:transport_id>/', views.SelectSeatsView.as_view(), name='select_seats'),
    
    # Itinerary
    path('trip/<int:trip_id>/itinerary/<str:plan_id>/', views.ItineraryDetailView.as_view(), name='itinerary_detail'),
    path('trip/<int:trip_id>/plan/<str:plan_id>/download-pdf/', views.DownloadItineraryPDFView.as_view(), name='download_itinerary_pdf'),
    
    # Activities
    path('trip/<int:trip_id>/plan/<str:plan_id>/add-activity/', views.AddActivityView.as_view(), name='add_activity'),
    path('trip/<int:trip_id>/plan/<str:plan_id>/remove-activity/', views.RemoveActivityView.as_view(), name='remove_activity'),
    
    # Real hotels API
    path('get-real-hotels/', views.GetRealHotelsView.as_view(), name='get_real_hotels'),
    path('search-real-hotels/<int:destination_id>/', views.SearchRealHotelsView.as_view(), name='search_real_hotels'),
    path('book-real-hotel/<int:trip_id>/', views.BookRealHotelView.as_view(), name='book_real_hotel'),
    
    # Clear trip
    path('clear-trip/', views.ClearTripDataView.as_view(), name='clear_trip'),
    
    # Destination search
    path('search-destinations/', views.DestinationSearchView.as_view(), name='search_destinations'),
    
    # Weather testing
    path('test-weather/', TestWeatherAPIView.as_view(), name='test_weather'),
    path('place/<int:place_id>/', PlaceDetailView.as_view(), name='place_detail'),
    
    # Destination browsing
    path('destinations/', DestinationListView.as_view(), name='destinations'),
    path('destinations/<int:destination_id>/', DestinationDetailView.as_view(), name='destination_detail'),
    path('destinations-autocomplete/', DestinationAutocompleteView.as_view(), name='destinations_autocomplete'),
    path('region/<int:region_id>/places/', RegionPlacesView.as_view(), name='region_places'),
    path('place/<int:place_id>/', PlaceDetailView.as_view(), name='place_detail'),
    # Dashboard analytics
    path('dashboard/trips/', TripListView.as_view(), name='trip_list'),
    path('dashboard/trips/upcoming/', UpcomingTripsView.as_view(), name='upcoming_trips'),
    path('dashboard/cost-analysis/', TripCostAnalysisView.as_view(), name='trip_cost_analysis'),
    path('dashboard/visited-destinations/', VisitedDestinationsView.as_view(), name='visited_destinations'),
    # Room selection and booking
    path('select-rooms/<int:trip_id>/', views.SelectRoomsView.as_view(), name='select_rooms'),
    path('get-available-rooms/<int:hotel_id>/', views.GetAvailableRoomsView.as_view(), name='get_available_rooms'),
    path('save-room-selection/<int:trip_id>/', views.SaveRoomSelectionView.as_view(), name='save_room_selection'),
    path('confirm-room-booking/<int:trip_id>/', views.ConfirmRoomBookingView.as_view(), name='confirm_room_booking'),
   

    path('confirm-room-booking/<int:trip_id>/', views.ConfirmRoomBookingView.as_view(), name='confirm_room_booking'),
]