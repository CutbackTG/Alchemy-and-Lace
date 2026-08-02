from django.conf import settings
from django.contrib import messages
import logging

from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.shortcuts import redirect, render

from catalog.models import Product

logger = logging.getLogger(__name__)


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
        else:
            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, "Please enter a valid email address.")
            else:
                if not settings.CONTACT_EMAIL:
                    messages.error(
                        request,
                        "The contact form is not configured yet. Please use the email address shown below.",
                    )
                else:
                    enquiry = EmailMessage(
                        subject=f"Website enquiry from {name}",
                        body=f"Name: {name}\nEmail: {email}\n\n{message}",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[settings.CONTACT_EMAIL],
                        reply_to=[email],
                    )
                    try:
                        enquiry.send(fail_silently=False)
                    except Exception:
                        logger.exception("Contact form email could not be sent")
                        messages.error(
                            request,
                            "Your message could not be sent just now. Please email us directly using the address shown on this page.",
                        )
                    else:
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
