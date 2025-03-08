from django.urls import path
from .views import (
    home,
    RegisterView, 
    LoginView, 
    LogoutView,
    ModuleInstanceView, 
    ProfessorRatingsView,
    AverageRatingView, 
    RateProfessorView,
)

urlpatterns = [
    path('', home, name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('module-instances/', ModuleInstanceView.as_view(), name='module-instances'),
    path('professor-ratings/', ProfessorRatingsView.as_view(), name='professor-ratings'),
    path('average/<str:professor_id>/<str:module_code>/', AverageRatingView.as_view(), name='average-rating'),
    path('rate/', RateProfessorView.as_view(), name='rate-professor'),
]