from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    category = models.CharField(max_length=20)

    def __str__(self):
        return self.category
    
class Language(models.Model):
    lang = models.CharField(max_length=20)

    def __str__(self):
        return self.lang

class AuctionListing(models.Model):
    item = models.CharField(max_length=30)
    description = models.CharField(max_length=300)
    lister = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="listings")
    date_time = models.DateTimeField(auto_now_add=True)
    image_url = models.CharField(max_length=1000)
    price = models.FloatField()
    active_status = models.BooleanField(default = True)
    genre = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="genre")
    language = models.ForeignKey(Language, on_delete=models.CASCADE, blank=True, null=True, related_name="language")
    watchlist = models.ManyToManyField(User, blank=True,  related_name="watchlist")
    winner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="winner")

    def __str__(self):
        return self.item
    
class Bid(models.Model):
    item = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, blank=True, null=True, related_name="bids_on_item")
    date_time = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="bids_from_user")

    def __str__(self):
        return f"${self.value}"


class Comment(models.Model):
    comment = models.TextField()
    commenter = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="comments_from_user")
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments_on_listing")