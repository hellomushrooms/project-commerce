from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<str:id>", views.listing, name="listing"),
    path("genres", views.genres, name="genres"),
    path("genres/<str:genre>", views.genre_results, name="genre_results"),
    path("addcomment/<str:id>", views.add_comment, name="add_comment"),
    path("togglewatchlist/<str:id>", views.toggle_watchlist, name="toggle_watchlist"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("closeauction/<str:id>", views.close_auction, name="close_auction")
]