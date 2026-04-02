<h1>My BCA 8th semester project</h1>
<p></p>
<p></p>
<h1>ACVS(Academic Credential Verification System)</h1>
<br><br>
# Academic Credential Verification System (ACVS)

## Overview

ACVS is a secure web application for issuing and verifying academic certificates using QR codes and UUID-based validation.

## Features

* Certificate issuance by universities
* Student certificate download
* QR-based verification
* PDF upload verification
* Audit logging
* Role-based authentication

## Tech Stack

* Django
* Bootstrap
* PostgreSQL
* Pillow, pyzbar, pdf2image
* Docker

## Setup

```bash
git clone https://github.com/Nenmpe/acvs.git
cd acvs
docker-compose up --build
```

## Usage

* University → Issue certificates
* Student → Download certificates
* Verifier → Upload QR/PDF to verify

## Future Scope

* Blockchain integration
* Full Multi-tenant support
