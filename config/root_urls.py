from django.contrib import admin
from django.urls import path, include, re_path



# schema_view = get_schema_view(
#     openapi.Info(
#         title="feed-service-swagger",
#         default_version="v1.0",
#         description="This is Feed Service's Swagger Docs",
#     ),
#     public=True,
#     permission_classes=[permissions.AllowAny],
# )


urlpatterns = [
    # [using swagger]
    # re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    # re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # [end-point]
    path('admin/', admin.site.urls),
    path('api/account/', include('accounts.urls')),
    path('api/auth/', include('auths.urls')),
    path('api/restaurant/', include('foodiehotspots.urls')),
]