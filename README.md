# MailCheck – Bulk Email Verification Web Application

A full-stack, beginner-friendly web application designed for verifying email address validity in batches of up to 100 addresses. Built for a college Software Development assignment, **MailCheck** performs genuine multi-stage verification including RFC syntax validation, live DNS Mail Exchange (MX) record lookups, RFC 7505 Null MX detection, and RFC 5321 fallback address routing.

---

## 1. Project Purpose & Highlights

Email delivery failure ("bounces") degrades sender reputation and clutters mailing lists. MailCheck provides an intuitive dashboard for users to paste email lists, inspect their routing capability, and download results as a structured CSV report.

Each address is deterministically classified into one of three statuses:
1. **Likely to Be Delivered:** Valid email syntax and active mail exchange routing (MX or A/AAAA fallback).
2. **Likely to Bounce:** Demonstrably invalid syntax, nonexistent domain (NXDOMAIN), explicit mail rejection (Null MX), or complete lack of mail routes.
3. **Unknown:** Temporary DNS resolver failures, query timeouts, or ambiguous server configurations.

> **Disclaimer:** MailCheck performs syntax and domain-level checks. A valid domain does not guarantee that a mailbox exists or will accept messages. Some mail servers hide mailbox information, and results cannot guarantee delivery.

---

## 2. Core Features

- **Multi-Line Batch Input:** Paste up to 100 email addresses, one per line.
- **Intelligent Deduplication:** Identifies and consolidates duplicate entries, displaying the duplicate count in the interface.
- **Real DNS Resolution:** Performs authentic DNS queries via `dnspython` with timeout protection (no hardcoded, random, or mocked results in production).
- **Interactive Metric Cards:** Summary cards displaying counts for Total Processed, Delivered, Bounced, and Unknown, which double as quick filters.
- **Dynamic Search & Filtering:** Filter results by status category or search dynamically by email address, domain, or reason.
- **One-Click CSV Export:** Download structured CSV reports (`Email`, `Status`, `Reason`, `Checks Performed`).
- **One-Click Sample Loader:** "Load Test Sample" button allows rapid demonstration of diverse test cases (valid emails, syntax errors, fake domains, reserved TLDs, and duplicates).
- **Responsive & Accessible Design:** Light dashboard interface with restrained blue accents, clear contrast ratios, and iconography that never relies on color alone.
- **Comprehensive Pytest Suite:** 27 automated backend tests with mocked DNS to guarantee 100% deterministic test execution.

---

## 3. Technology Stack

- **Frontend:** React 19, TypeScript, Vite, Lucide Icons.
- **Backend API:** Python 3.11+, Flask 3.1, `dnspython` 2.7, `email-validator` 2.2, `flask-cors`.
- **Production Server:** Gunicorn WSGI.
- **Testing:** Pytest 8.3 & `pytest-mock`.
- **Submission PDF Generation:** ReportLab 4.2.
- **Hosting / Deployment:** Render (via unified web service blueprint `render.yaml`).

---

## 4. Project Structure

```text
mailcheck/
├── backend/
│   ├── app.py                     # Flask API routes, CORS, validation, static asset serving
│   ├── verifier.py                # Core verification logic (Syntax, DNS MX, A/AAAA fallback)
│   ├── requirements.txt           # Python backend dependencies
│   ├── pytest.ini                 # Pytest configuration
│   ├── tests/
│   │   ├── test_verifier.py       # Unit tests for verifier functions with mocked DNS
│   │   └── test_api.py            # Integration tests for Flask endpoints and CORS
│   └── venv/                      # Local Python virtual environment
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx         # Brand header and API health status badge
│   │   │   ├── EmailInput.tsx     # Textarea, sample loader, line counter, clear/verify buttons
│   │   │   ├── SummaryCards.tsx   # Interactive count cards for metrics & filtering
│   │   │   ├── ResultsTable.tsx   # Results table with search, badges, copy button, CSV export
│   │   │   ├── Disclaimer.tsx     # Mandatory delivery disclaimer banner
│   │   │   └── ArchitectureInfo.tsx # Collapsible methodology & assignment reference panel
│   │   ├── types.ts               # Shared TypeScript interface definitions
│   │   ├── App.tsx                # Main application state and API coordination
│   │   ├── main.tsx               # React root entrypoint
│   │   └── index.css              # Custom responsive stylesheet (restrained blue palette)
│   ├── index.html                 # HTML shell with meta tags and SVG favicon
│   ├── package.json               # Frontend dependencies and scripts
│   ├── vite.config.ts             # Vite build and dev server proxy config
│   └── .env.example               # Frontend environment variable template
├── generate_submission_pdf.py     # Script to generate the required 1-page assignment submission PDF
├── render.yaml                    # Render Blueprint configuration for free cloud deployment
├── .gitignore                     # Git ignore rules for Python, Node, Vite, and environments
└── README.md                      # Complete project documentation
```

---

## 5. Prerequisites

Before running locally, ensure you have installed:
- **Python:** 3.10 or newer (tested with Python 3.11 – 3.13)
- **Node.js:** v18 or newer (tested with Node v24)
- **Git**

---

## 6. Step-by-Step Local Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/mailcheck.git
cd mailcheck
```

### 2. Set up Backend
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
.\venv\Scripts\activate.bat
# macOS / Linux:
source venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt
```

### 3. Set up Frontend
Open a second terminal window in the project root:
```bash
cd frontend

# Install dependencies
npm install
```

---

## 7. Running the Application Locally

### Running Backend (Terminal 1)
```bash
cd backend
# With virtual environment active:
python app.py
```
The backend API starts at `http://127.0.0.1:5000`.

### Running Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```
The Vite development server starts at `http://localhost:5173`. 
The Vite server automatically proxies requests starting with `/api` to `http://127.0.0.1:5000`.

---

## 8. Backend API Documentation

### 1. Health Check
- **Endpoint:** `GET /api/health`
- **Purpose:** Diagnostic health check and uptime monitor.
- **Response Example:**
```json
{
  "status": "healthy",
  "service": "mailcheck-backend",
  "max_batch_size": 100,
  "version": "1.0.0"
}
```

### 2. Verify Email Batch
- **Endpoint:** `POST /api/verify`
- **Headers:** `Content-Type: application/json`
- **Request Body Example:**
```json
{
  "emails": [
    "support@github.com",
    "admissions@stanford.edu",
    "malformed-syntax-email",
    "user@nonexistent-domain-404.org",
    "support@github.com"
  ]
}
```
- **Success Response (200 OK):**
```json
{
  "results": [
    {
      "email": "support@github.com",
      "status": "likely_delivered",
      "reason": "Domain has valid mail exchange records (1 MX host(s) found).",
      "checks_performed": ["syntax", "dns_mx"]
    },
    {
      "email": "admissions@stanford.edu",
      "status": "likely_delivered",
      "reason": "Domain has valid mail exchange records (5 MX host(s) found).",
      "checks_performed": ["syntax", "dns_mx"]
    },
    {
      "email": "malformed-syntax-email",
      "status": "likely_bounce",
      "reason": "Missing '@' symbol in email address.",
      "checks_performed": ["syntax"]
    },
    {
      "email": "user@nonexistent-domain-404.org",
      "status": "likely_bounce",
      "reason": "Domain does not exist (NXDOMAIN).",
      "checks_performed": ["syntax", "dns_lookup"]
    }
  ],
  "summary": {
    "total_submitted": 5,
    "unique_processed": 4,
    "duplicates_removed": 1,
    "likely_delivered": 2,
    "likely_bounce": 2,
    "unknown": 0
  }
}
```
- **Error Responses:**
  - `400 Bad Request`: Empty list, non-list payload, malformed JSON, or missing `emails` key.
  - `400 Bad Request`: Batch limit exceeded (submitted > 100 emails).
  - `500 Internal Server Error`: Unhandled internal exception (generic message returned; internal traces are never exposed to the client).

---

## 9. Running Automated Tests

MailCheck includes 27 comprehensive automated tests verifying syntax parsing, DNS MX lookups, RFC fallback routing, batch limits, and API edge cases. All external DNS interactions are mocked to guarantee deterministic, offline execution.

To execute the test suite:
```bash
cd backend
# Make sure your virtual environment is active:
pytest -v
```

Expected output:
```text
============================= test session starts =============================
collected 27 items

tests/test_api.py::TestHealthEndpoint::test_health_check_returns_200 PASSED
tests/test_api.py::TestVerifyEndpointValidation::test_non_json_request_returns_400 PASSED
tests/test_api.py::TestVerifyEndpointValidation::test_missing_emails_field_returns_400 PASSED
tests/test_api.py::TestVerifyEndpointValidation::test_emails_not_a_list_returns_400 PASSED
tests/test_api.py::TestVerifyEndpointValidation::test_empty_emails_list_returns_400 PASSED
tests/test_api.py::TestVerifyEndpointValidation::test_oversized_batch_returns_400 PASSED
tests/test_api.py::TestVerifyEndpointSuccess::test_verify_valid_and_invalid_emails PASSED
tests/test_api.py::TestVerifyEndpointSuccess::test_cors_headers_present PASSED
tests/test_verifier.py::TestEmailSyntaxValidation::test_valid_standard_email PASSED
tests/test_verifier.py::TestEmailSyntaxValidation::test_valid_email_with_dots_and_plus PASSED
tests/test_verifier.py::TestEmailSyntaxValidation::test_invalid_email_missing_at PASSED
tests/test_verifier.py::TestEmailSyntaxValidation::test_invalid_email_missing_local PASSED
tests/test_verifier.py::TestEmailSyntaxValidation::test_invalid_email_missing_domain PASSED
tests/test_verifier.py::TestEmailSyntaxValidation::test_invalid_email_spaces_and_special_chars PASSED
tests/test_verifier.py::TestEmailSyntaxValidation::test_invalid_email_empty_or_none PASSED
tests/test_verifier.py::TestEmailSyntaxValidation::test_invalid_email_exceeds_max_length PASSED
tests/test_verifier.py::TestEmailSyntaxValidation::test_invalid_reserved_tld PASSED
tests/test_verifier.py::TestDNSAndDomainVerification::test_domain_with_valid_mx_records PASSED
tests/test_verifier.py::TestDNSAndDomainVerification::test_domain_with_null_mx_record_rfc7505 PASSED
tests/test_verifier.py::TestDNSAndDomainVerification::test_domain_nonexistent_nxdomain PASSED
tests/test_verifier.py::TestDNSAndDomainVerification::test_domain_no_mx_but_valid_a_fallback_rfc5321 PASSED
tests/test_verifier.py::TestDNSAndDomainVerification::test_domain_no_mx_and_no_fallback_records PASSED
tests/test_verifier.py::TestDNSAndDomainVerification::test_dns_timeout_returns_unknown PASSED
tests/test_verifier.py::TestDNSAndDomainVerification::test_dns_temporary_resolver_failure_returns_unknown PASSED
tests/test_verifier.py::TestBatchVerification::test_batch_verification_with_various_statuses PASSED
tests/test_verifier.py::TestBatchVerification::test_empty_batch_raises_value_error PASSED
tests/test_verifier.py::TestBatchVerification::test_oversized_batch_raises_value_error PASSED

============================= 27 passed in 0.40s ==============================
```

---

## 10. Verification Algorithm & Methodology

The verification pipeline processes addresses through three deterministic steps:

```
[Email Input] ──> [1. Syntax Check (RFC 5321/5322)]
                        │
         ┌──────────────┴──────────────┐
     [Invalid]                      [Valid]
         │                             │
   Likely to Bounce           [2. DNS Query (dnspython)]
                                       │
                      ┌────────────────┼────────────────┐
                  [Null MX]       [MX Found]      [No MX]
                      │                │                │
               Likely to Bounce   Likely to       [RFC 5321 Fallback]
                                  Delivered             │
                                           ┌────────────┴────────────┐
                                      [A/AAAA Found]           [No A/AAAA]
                                           │                        │
                                      Likely to              Likely to Bounce
                                      Delivered
```

### Step 1: Syntax Validation
- Validates structural rules per **RFC 5322** and **RFC 6531**.
- Validates local part ($\le 64$ characters) and total email length ($\le 254$ characters) per **RFC 5321**.
- Rejects addresses using reserved testing TLDs (`.invalid`, `.test`, `.localhost`) per **RFC 2606**.

### Step 2: Domain and DNS Verification
- Extracts domain name and sets DNS query timeouts (3.0s query timeout, 4.0s lifetime).
- Queries `MX` records via `dnspython`.
- **RFC 7505 Null MX Detection:** If the domain returns a single MX record with preference 0 and target `.` (Null MX), the domain has explicitly declared that it does not accept email. Result: `likely_bounce`.
- **RFC 5321 Section 5.1 Fallback Routing:** If no MX records exist (`NoAnswer`), standard email routing rules require checking for address (`A` or `AAAA`) records. If address records exist, an implicit mail route is present. Result: `likely_delivered`. If neither exists, result: `likely_bounce`.
- **DNS Failures:** `NXDOMAIN` (domain does not exist) is classified as `likely_bounce`. DNS timeouts and `NoNameservers` resolver errors are classified as `unknown`.

### Step 3: SMTP Verification & Hosting Restrictions
- **Why SMTP port 25 is restricted:** Free hosting providers (Render, Vercel, Railway, AWS Free Tier, DigitalOcean) and consumer ISPs block outbound TCP port 25 to prevent spam and abuse.
- **Ethical & Technical Limits:** Connecting to arbitrary third-party SMTP servers to probe individual recipient mailboxes triggers spam alarms, rate-limiting, greylisting, and IP blocklisting. Furthermore, modern mail providers (such as Gmail, Outlook, and Yahoo) configure catch-all or silent acceptance behavior, making mailbox probes inconclusive without sending actual messages.
- **Implementation Disclosure:** The deployed version of MailCheck intentionally avoids intrusive SMTP connections and relies on syntax validation and DNS mail-routing analysis. When DNS information is incomplete or inconclusive, MailCheck truthfully returns `unknown`.

---

## 11. Deployment Instructions (Render Free Tier)

MailCheck is configured for deployment as a **single unified Web Service on Render** using the included `render.yaml`. This ensures zero CORS issues and fits within Render's free tier.

### Option A: Deploy via Render Blueprint (Recommended)
1. Push your repository to your GitHub account:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of MailCheck project"
   git remote add origin https://github.com/<your-username>/mailcheck.git
   git branch -M main
   git push -u origin main
   ```
2. Log in to [Render](https://render.com).
3. Click **New +** and select **Blueprint**.
4. Connect your GitHub repository.
5. Render detects `render.yaml` and sets up the service automatically:
   - **Build Command:** `cd frontend && npm install && npm run build && cd ../backend && pip install -r requirements.txt`
   - **Start Command:** `cd backend && gunicorn app:app --bind 0.0.0.0:$PORT`
6. Click **Apply**. Render will build the React frontend, place the production assets in `frontend/dist`, and run Flask via Gunicorn serving both the API and the user interface.

### Option B: Deploy Manually as a Render Web Service
1. In Render, select **New +** -> **Web Service**.
2. Select your repository and choose **Python** as runtime.
3. Set **Build Command**:
   ```bash
   cd frontend && npm install && npm run build && cd ../backend && pip install -r requirements.txt
   ```
4. Set **Start Command**:
   ```bash
   cd backend && gunicorn app:app --bind 0.0.0.0:$PORT
   ```
5. Add Environment Variables:
   - `PYTHON_VERSION`: `3.11.9`
   - `NODE_VERSION`: `20.18.0`
   - `FLASK_ENV`: `production`
   - `CORS_ORIGIN`: `*`
   - `MAX_BATCH_SIZE`: `100`

---

## 12. Generating the Assignment Submission PDF

Once your GitHub repository is created and your live web application is deployed on Render, generate your official, 1-page academic submission PDF:

```bash
# In the project root with backend/venv activated:
python generate_submission_pdf.py --live-url "https://your-app-name.onrender.com" --repo-url "https://github.com/your-username/mailcheck" --student-name "Your Name"
```

This outputs `MailCheck_Project_Submission.pdf` formatted with:
- Project title: **MailCheck – Bulk Email Verification Tool**
- Project summary & feature overview
- Clickable **Live Application URL**
- Clickable **GitHub Repository URL**
- Architecture and testing metadata
- Delivery disclaimer

---

## 13. License & Academic Integrity

This project was developed for a college Software Development assignment. All code and verification logic are genuine and follow RFC specifications.
