from django.urls import path
from .views import (
    RegisterView, 
    LoginView, 
    LogoutView,
    ModuleInstanceList, 
    ProfessorRatingsView,
    AverageRatingForModule, 
    RateProfessor,
    home,
)

urlpatterns = [
    path('', home, name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('module-instances/', ModuleInstanceList.as_view(), name='module-instances'),
    path('professor-ratings/', ProfessorRatingsView.as_view(), name='professor-ratings'),
    path('average/<str:professor_id>/<str:module_code>/', AverageRatingForModule.as_view(), name='average-rating'),
    path('rate/', RateProfessor.as_view(), name='rate-professor'),
]