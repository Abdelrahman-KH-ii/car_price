from django.contrib import admin
from django.urls import path, include
from predictor import views as pred_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', pred_views.home, name='home'),
    path('predict/', pred_views.predict_view, name='predict'),
    path('predict/result/', pred_views.predict_result, name='predict_result'),
    path('api/models/', pred_views.get_models_api, name='get_models'),
    path('accounts/', include('accounts.urls')),
]
