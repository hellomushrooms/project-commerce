from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required


from .models import User, Category, AuctionListing, Language, Bid, Comment


def index(request):
    active_listings = AuctionListing.objects.filter(active_status=True)
    return render(request, "auctions/index.html", {
        "active_listings": active_listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    if request.method == "POST":
        user = request.user
        name = request.POST['item-name']
        description = request.POST['description']
        image = request.POST['image']
        category_name = request.POST['category']
        category = Category.objects.get(category=category_name)
        language_name = request.POST['language']
        language = Language.objects.get(lang = language_name)
        price = request.POST['starting-bid']
        l = AuctionListing(
            item=name, 
            description=description, 
            image_url=image, 
            lister=user, 
            price = float(price), 
            genre=category,
            language=language
        )
        l.save()
        return HttpResponseRedirect(reverse(index))
    else:
        categories = Category.objects.all()
        languages = Language.objects.all()
        return render(request, "auctions/create-listing.html", {
            "categories": categories,
            "languages": languages
        })
    
def listing(request, id):
    if request.method == "POST":
        bid = request.POST['bid']
        user = request.user
        item_id = request.POST['listing-id']
        item = AuctionListing.objects.get(id=item_id)
        if(float(bid) > item.price):
            b = Bid(
                item=item, 
                value=float(bid), 
                bidder=user
            )
            b.save()
            item.price = float(bid)
            item.save()
            messages.success(request, "Your bid has been saved.")
            return HttpResponseRedirect(reverse("listing", args=[item_id]))

        else:
            messages.error(request, "Your bid is too low.")
            return HttpResponseRedirect(reverse("listing", args=[item_id]))

    else:
        listing = AuctionListing.objects.get(id=id)
        bids = Bid.objects.filter(item=listing)
        highestbid = bids.order_by('-value').first()
        comments = Comment.objects.filter(listing=listing)
        user = request.user
        user_watchlisted = request.user in listing.watchlist.all()
        closable = False
        if bids:
            closable = True
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "bids": bids,
            "num_bids": len(bids),
            "comments": comments,
            "user": user,
            "user_watchlisted": user_watchlisted,
            "highestbid": highestbid,
            "closable": closable
        })
    
def genres(request):
    genres = Category.objects.all()
    return render(request, "auctions/genres.html", {
        "genres": genres
    })

def genre_results(request, genre):
    genre = Category.objects.get(category=genre)
    movies = AuctionListing.objects.filter(genre=genre)
    return render(request, "auctions/genre-results.html", {
        "results": movies,
        "genre": genre
    })

@login_required
def add_comment(request, id):
    comment = request.POST['comment']
    user = request.user
    listing = AuctionListing.objects.get(id=id)
    c = Comment(comment=comment, commenter=user, listing=listing)
    c.save()
    return HttpResponseRedirect(reverse("listing", args=[id]))

@login_required
def toggle_watchlist(request, id):
    user = request.user
    listing = AuctionListing.objects.get(id=id)
    if user in listing.watchlist.all():
        listing.watchlist.remove(user)
    else:
        listing.watchlist.add(user)
    return HttpResponseRedirect(reverse("listing", args=[id]))

@login_required
def watchlist(request):
    user = request.user
    listings = AuctionListing.objects.filter(watchlist=user)
    return render(request, "auctions/watchlist.html", {
        "results": listings
    })

@login_required
def close_auction(request, id):
    if request.method == 'POST':
        listing = AuctionListing.objects.get(id=id)
        if Bid.objects.filter(item=listing):
            listing = AuctionListing.objects.get(id=id)
            listing.active_status = False
            highestbid = Bid.objects.filter(item=listing).order_by('-value').first()
            listing.winner = highestbid.bidder
            listing.save()
            return HttpResponseRedirect(reverse("listing", args=[id]))
        else:
            return HttpResponseRedirect(reverse("listing", args=[id]))