# Gallery-only deployment

The public site now contains only:

- Home
- Gallery and gallery detail pages
- Kimono fabric history
- Business contact
- Django admin for private product/gallery management

Customer accounts, social login, carts, checkout, Stripe, orders, reviews, profiles, and the custom manager dashboard have been removed from the public application.

## Heroku configuration

Set these Config Vars:

- `DJANGO_SECRET_KEY`: a long random secret
- `DJANGO_DEBUG`: `False`
- `DJANGO_ALLOWED_HOSTS`: comma-separated production domains
- `DJANGO_CSRF_TRUSTED_ORIGINS`: comma-separated HTTPS origins, including `https://`
- `CONTACT_EMAIL`: destination for business enquiries
- Cloudinary and database variables already used by the app
- SMTP variables if the contact form should send mail

Run after deployment:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
```

## Browser "unsafe" warning

The code now redirects to HTTPS and enables secure cookies, HSTS, MIME sniffing protection, a strict referrer policy, and frame denial in production. A browser interstitial can still persist when the custom domain's DNS or TLS certificate is invalid, expired, not issued yet, or the domain has been flagged by a browser security service. That must be corrected in Heroku's Domains settings and at the DNS provider; application code alone cannot remove a certificate or reputation warning.
