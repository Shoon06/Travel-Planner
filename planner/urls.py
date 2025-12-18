from django.urls import path
from . import views

app_name = 'planner'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('plan/', views.PlanTripView.as_view(), name='plan'),
    # URL to search destinations (used by the autocomplete in plan.html)
    path('search-destinations/', views.SearchDestinationsView.as_view(), name='search_destinations'),
    # URL to view and select a hotel for a specific trip
    path('plan/<int:trip_id>/hotels/', views.SelectHotelView.as_view(), name='select_hotel'),
    # URL to save the selected hotel
    path('plan/<int:trip_id>/hotels/select/', views.SaveHotelView.as_view(), name='save_hotel'),
    # URL to choose a transport type (Flight, Bus, Car)
    path('plan/<int:trip_id>/transport/', views.SelectTransportCategoryView.as_view(), name='select_transport_category'),
    # URL to see the list of options for a chosen transport type
    path('plan/<int:trip_id>/transport/list/', views.SelectTransportView.as_view(), name='select_transport'),
    # URL to save the selected transport
    path('plan/<int:trip_id>/transport/save/', views.SaveTransportView.as_view(), name='save_transport'),
    # URL to select seats for flight or bus
    path('plan/<int:trip_id>/transport/<int:transport_id>/seats/', views.SelectSeatsView.as_view(), name='select_seats'),
]