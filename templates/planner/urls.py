from django.urls import path
from . import views
from .views import GetRealHotelsView, BookRealHotelView
app_name = 'planner'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('plan/', views.PlanTripView.as_view(), name='plan'),
    path('plan/<int:trip_id>/hotels/', views.SelectHotelView.as_view(), name='select_hotel'),
    path('plan/<int:trip_id>/hotels/select/', views.SaveHotelView.as_view(), name='save_hotel'),
    path('plan/<int:trip_id>/transport/', views.SelectTransportCategoryView.as_view(), name='select_transport_category'),
    path('plan/<int:trip_id>/transport/list/', views.SelectTransportView.as_view(), name='select_transport'),
    path('plan/<int:trip_id>/transport/save/', views.SaveTransportView.as_view(), name='save_transport'),
    path('search-destinations/', views.SearchDestinationsView.as_view(), name='search_destinations'),
    path('get-real-hotels/', GetRealHotelsView.as_view(), name='get_real_hotels'),
    path('trip/<int:trip_id>/book-real-hotel/', BookRealHotelView.as_view(), name='book_real_hotel'),
]