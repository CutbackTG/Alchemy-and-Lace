from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render

from catalog.models import Product


def index(request):
    featured_products = Product.objects.filter(is_active=True).prefetch_related("images")[:6]
    return render(
        request,
        "home/index.html",
        {"featured_products": featured_products, "active_menu_item": "home"},
    )


def contact(request):
    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        email = (request.POST.get("email") or "").strip()
        message = (request.POST.get("message") or "").strip()
        website = (request.POST.get("website") or "").strip()  # honeypot

        if website:
            return redirect("home:contact")

        if not name or not email or not message:
            messages.error(request, "Please complete your name, email, and message.")
        elif not settings.CONTACT_EMAIL:
            messages.error(
                request,
                "The contact form is not configured yet. Please use the email address shown below.",
            )
        else:
            send_mail(
                subject=f"Website enquiry from {name}",
                message=f"Name: {name}\nEmail: {email}\n\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            messages.success(request, "Thank you. Your enquiry has been sent.")
            return redirect("home:contact")

    return render(
        request,
        "home/contact.html",
        {
            "active_menu_item": "contact",
            "contact_email": settings.CONTACT_EMAIL,
        },
    )


def kimono_history(request):
    return render(
        request,
        "home/kimono_history.html",
        {"active_menu_item": "kimono_history"},
    )
