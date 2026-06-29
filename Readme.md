<h1>My BCA 8th semester project</h1>
<p></p>
<p></p>
<h1>ACVS(Academic Credential Verification System)</h1>
<br><br>
# Academic Credential Verification System (ACVS)

## Overview

ACVS is a Django-based academic credential issuance and verification application. It enables university administrators to create student accounts, issue digitally signed certificates, generate QR codes, and store credential proofs on the blockchain. Verifiers can validate credentials by scanning QR codes or uploading certificate files.

## Key Features

* Role-based access control with Super Admin, University Admin, Student, and Verifier roles.
* University Admin dashboard for student creation and credential issuance.
* Student dashboard for certificate download and status review.
* Verifier registration and credential verification workflows.
* QR code-based verification with UUID-linked credential records.
* PDF upload verification for credential files containing QR codes.
* Digital credential hashing, RSA signature verification, and blockchain transaction validation.
* Audit logging of student creation, credential issuance, and verification events.

## Architecture

* Django project root: `app/`
* Main apps:
  * `accounts` — custom user model, roles, registration, dashboards, password management.
  * `credentials` — credential creation, PDF generation, QR code logic, upload verification.
  * `verification` — credential verification endpoint.
  * `universities` — university metadata.
  * `base` — home page, login/logout, registration views.
  * `core` — middleware, blockchain integration, security utilities.
* Database: PostgreSQL
* File storage: media files under `media/` for certificates and QR codes.

## User Roles

* `SUPER_ADMIN` — access to Django admin panel and site-wide management.
* `UNIVERSITY_ADMIN` — create students, issue credentials, view university statistics.
* `STUDENT` — view and download issued certificates.
* `VERIFIER` — register via public form and verify credentials.

## Requirements

* Python 3.12+
* Django 6.x
* PostgreSQL
* Docker and Docker Compose (recommended)
* System libraries for Pillow, WeasyPrint, zbar, poppler, and pango.

## Dependencies

Dependencies are listed in `requirements.txt` and include:

* Django
* djangorestframework
* djangorestframework-simplejwt
* psycopg2-binary
* Pillow
* pyzbar
* pdf2image
* qrcode
* django-filter
* cryptography
* weasyprint
* web3
* eth-account
* python-dotenv
* django-environ

## Environment Configuration

Create a `.env` file in the project root with the following values:

```dotenv
SECRET_KEY=your-secret-key
DEBUG=True
BASE_URL=http://localhost:8000
DB_NAME=acvs
DB_USER=acvs_user
DB_PASSWORD=acvs_pass
DB_HOST=db
DB_PORT=5432
BLOCKCHAIN_RPC_URL=https://your-ethereum-node.example
BLOCKCHAIN_ACCOUNT=0xYourAccountAddress
BLOCKCHAIN_PRIVATE_KEY=your-private-key
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
```

> Note: `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` are required by Django email settings. If you do not need email features, you can still leave these set to placeholder values.

## Generate a Django Secret Key

Use one of the commands below to create a secure secret key for your `.env` file.

From the project root:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Or with Docker Compose:

```bash
docker compose run --rm web python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the generated value into `SECRET_KEY` in your `.env` file.

## Required Files

The application signs credentials with RSA keys. Ensure the following files are available in the working directory used by `manage.py` or your container runtime:

* `private_key.pem`
* `public_key.pem`

The application uses `private_key.pem` to sign credentials and `public_key.pem` to verify digital signatures.

## Docker Setup

Build and run the application with Docker Compose:

```bash
docker-compose up --build
```

This starts two services:

* `db` — PostgreSQL database on port `5432`
* `web` — Django app on port `8000`

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/Nenmpe/acvs.git
cd acvs
```
2. Create and configure `.env`.
3. Build and start Docker:
```bash
docker-compose up --build
```
4. Apply migrations, collectstatic and create a superuser:
```bash
docker exec -it acvs_web python manage.py migrate
docker compose -it acvs_web python manage.py collectstatic --noinput
docker exec -it acvs_web python manage.py createsuperuser
```
5. Visit `http://localhost:8000`.

## Application URLs

* Home: `/`
* Login: `/login/`
* Register Verifier: `/register/`
* Logout: `/logout/`
* Dashboard redirect: `/accounts/dashboard/`
* Create student (University Admin): `/accounts/create-student/`
* Student dashboard: `/accounts/student-dashboard/`
* University dashboard: `/accounts/university-dashboard/`
* Verifier dashboard: `/accounts/verifier-dashboard/`
* Issue credential: `/credentials/issue-credential/`
* Download certificate: `/credentials/download/<credential_id>/`
* Upload and verify file: `/credentials/upload-verify/`
* Verify credential by UUID: `/credential/verify/<uuid>/`
* Admin panel: `/admin/`

## Credential Workflow

1. University Admin logs in and creates students.
2. The admin issues a credential by selecting a student and entering degree details.
3. The system generates an SHA-256 credential hash and a QR code containing the credential UUID.
4. The credential hash is signed with RSA and stored on the blockchain as transaction data.
5. A PDF certificate is generated and stored in `media/certificates/`.
6. Verifiers validate credentials by scanning QR codes or uploading certificate files.

## Blockchain Integration

* Blockchain connectivity is optional but required to issue credentials successfully.
* The project uses `web3.py` and stores credential hash data in an Ethereum transaction.
* Verification checks chain state, transaction sender, and the stored hash.
* If blockchain is unavailable, the app may still perform local integrity and signature validation.

## Notes

* The application currently requires PostgreSQL environment configuration and a running blockchain node URL.
* The `app/config/settings.py` file reads `.env` values through `django-environ`.
* Media files are served from `media/`, and uploaded/downloaded certificates are stored there.

## Future Improvements

* Multi-tenant university support
* Enhanced blockchain transaction metadata
* Admin-facing credential revocation UI
* More robust key management for production

