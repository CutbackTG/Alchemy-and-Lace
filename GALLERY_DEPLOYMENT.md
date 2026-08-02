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

## Contact form email

Heroku does not provide an outgoing mail server automatically. Configure an SMTP provider in Heroku Config Vars:

- `CONTACT_EMAIL`: inbox that receives enquiries
- `DEFAULT_FROM_EMAIL`: verified sender address at your mail provider
- `EMAIL_HOST`: SMTP hostname supplied by the provider
- `EMAIL_PORT`: usually `587` for TLS or `465` for SSL
- `EMAIL_HOST_USER`: SMTP username
- `EMAIL_HOST_PASSWORD`: SMTP password or app password
- `EMAIL_USE_TLS`: `True` for port 587
- `EMAIL_USE_SSL`: `True` for port 465, with `EMAIL_USE_TLS=False`

Do not enable TLS and SSL at the same time. The sender address normally must be verified by the SMTP provider. The visitor's address is set as Reply-To rather than From, which avoids SPF and DMARC rejection.
