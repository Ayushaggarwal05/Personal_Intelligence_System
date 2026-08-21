import os
import shutil
import tempfile
import pytest
from app.tools.parsers.django_parser import (
    is_django_project,
    parse_django_urls_recursive,
    extract_django_routes_for_project
)

@pytest.fixture
def temp_django_project():
    """Creates a temporary mock Django project structure with nested app urls.py files."""
    temp_dir = tempfile.mkdtemp()
    
    # Create manage.py
    with open(os.path.join(temp_dir, "manage.py"), "w", encoding="utf-8") as f:
        f.write("# Django manage.py\n")

    # Create root config/urls.py
    config_dir = os.path.join(temp_dir, "config")
    os.makedirs(config_dir, exist_ok=True)
    root_urls = os.path.join(config_dir, "urls.py")
    with open(root_urls, "w", encoding="utf-8") as f:
        f.write(
            "from django.urls import path, include\n\n"
            "urlpatterns = [\n"
            "    path('api/v1/users/', include('apps.users.urls')),\n"
            "    path('api/v1/orders/', include('apps.orders.urls')),\n"
            "    path('health/', lambda r: None, name='health'),\n"
            "]\n"
        )

    # Create apps/users/urls.py
    users_dir = os.path.join(temp_dir, "apps", "users")
    os.makedirs(users_dir, exist_ok=True)
    with open(os.path.join(users_dir, "urls.py"), "w", encoding="utf-8") as f:
        f.write(
            "from django.urls import path\n"
            "from . import views\n\n"
            "urlpatterns = [\n"
            "    path('', views.UserListView.as_view(), name='user-list'),\n"
            "    path('<int:pk>/', views.user_detail, name='user-detail'),\n"
            "]\n"
        )

    # Create apps/orders/urls.py
    orders_dir = os.path.join(temp_dir, "apps", "orders")
    os.makedirs(orders_dir, exist_ok=True)
    with open(os.path.join(orders_dir, "urls.py"), "w", encoding="utf-8") as f:
        f.write(
            "from django.urls import path\n"
            "from . import views\n\n"
            "urlpatterns = [\n"
            "    path('checkout/', views.checkout_view, name='checkout'),\n"
            "]\n"
        )

    yield temp_dir

    shutil.rmtree(temp_dir)

def test_is_django_project_detection(temp_django_project):
    """Verifies that Django project detection correctly identifies manage.py / urls.py."""
    assert is_django_project(temp_django_project) is True
    
    empty_dir = tempfile.mkdtemp()
    try:
        assert is_django_project(empty_dir) is False
    finally:
        shutil.rmtree(empty_dir)

def test_recursive_django_route_extraction(temp_django_project):
    """Verifies that recursive urls.py parsing correctly stitches prefixes across app folders."""
    routes = extract_django_routes_for_project(temp_django_project)
    
    assert len(routes) >= 3
    signatures = [r["signature"] for r in routes]
    
    # Verify concatenated URL paths
    assert any("/api/v1/users/" in sig for sig in signatures)
    assert any("/api/v1/users/<int:pk>/" in sig for sig in signatures)
    assert any("/api/v1/orders/checkout/" in sig for sig in signatures)
    assert any("/health/" in sig for sig in signatures)
    
    # Check symbol types
    for r in routes:
        assert r["type"] == "route"
        assert r["name"].startswith("GET") or r["name"].startswith("POST")
