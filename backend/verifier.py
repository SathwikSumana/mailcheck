"""Email verification module for MailCheck.

Performs syntax validation and DNS/MX record lookups according to RFC standards:
- RFC 5321 / RFC 5322 (Email syntax & fallback A/AAAA routing)
- RFC 7505 (Null MX handling for domains that explicitly reject mail)
"""

import re
from typing import Any, Dict, List, Optional
import dns.resolver
from email_validator import EmailNotValidError, validate_email


# Status constants
STATUS_LIKELY_DELIVERED = "likely_delivered"
STATUS_LIKELY_BOUNCE = "likely_bounce"
STATUS_UNKNOWN = "unknown"

# Common disposable or reserved top-level domains that definitely cannot receive mail
INVALID_TLDS = {"invalid", "test", "example", "localhost"}


def validate_syntax(email: str) -> Dict[str, Any]:
    """Validate email syntax using email-validator with fallback regex checks.
    
    Returns:
        dict with keys: 'valid' (bool), 'domain' (str), 'normalized' (str), 'reason' (str)
    """
    if not email or not isinstance(email, str):
        return {
            "valid": False,
            "domain": "",
            "normalized": "",
            "reason": "Email address is empty or not a valid text string.",
        }

    email_clean = email.strip()
    if not email_clean:
        return {
            "valid": False,
            "domain": "",
            "normalized": "",
            "reason": "Email address is empty.",
        }

    # Basic structural check
    if "@" not in email_clean:
        return {
            "valid": False,
            "domain": "",
            "normalized": email_clean,
            "reason": "Missing '@' symbol in email address.",
        }

    parts = email_clean.rsplit("@", 1)
    local_part, domain = parts[0], parts[1]

    if not local_part:
        return {
            "valid": False,
            "domain": domain,
            "normalized": email_clean,
            "reason": "Missing username/local part before '@'.",
        }

    if not domain:
        return {
            "valid": False,
            "domain": "",
            "normalized": email_clean,
            "reason": "Missing domain name after '@'.",
        }

    # RFC 5321 length limits
    if len(email_clean) > 254:
        return {
            "valid": False,
            "domain": domain,
            "normalized": email_clean,
            "reason": "Email address exceeds maximum length of 254 characters (RFC 5321).",
        }

    if len(local_part) > 64:
        return {
            "valid": False,
            "domain": domain,
            "normalized": email_clean,
            "reason": "Local part exceeds maximum length of 64 characters (RFC 5321).",
        }

    # Use email-validator library for rigorous syntax checking (RFC 5322 + RFC 6531)
    try:
        validation_result = validate_email(
            email_clean,
            check_deliverability=False,  # We perform our own DNS checks separately
            test_environment=False,
        )
        normalized_email = validation_result.normalized
        ascii_domain = validation_result.ascii_domain or domain.lower()
        
        # Check for RFC 2606 reserved TLDs
        tld = ascii_domain.split(".")[-1]
        if tld in INVALID_TLDS:
            return {
                "valid": False,
                "domain": ascii_domain,
                "normalized": normalized_email,
                "reason": f"Domain uses reserved non-routable top-level domain '.{tld}'.",
            }

        return {
            "valid": True,
            "domain": ascii_domain,
            "normalized": normalized_email,
            "reason": "Valid email syntax.",
        }
    except EmailNotValidError as err:
        return {
            "valid": False,
            "domain": domain.lower(),
            "normalized": email_clean,
            "reason": f"Invalid email format: {str(err)}",
        }
    except Exception as err:
        return {
            "valid": False,
            "domain": domain.lower(),
            "normalized": email_clean,
            "reason": f"Invalid email format: {str(err)}",
        }


def check_domain_dns(
    domain: str,
    resolver: Optional[dns.resolver.Resolver] = None,
    dns_timeout: float = 3.0,
) -> Dict[str, Any]:
    """Perform DNS lookup for MX records and RFC 5321 A/AAAA fallback routes.
    
    Returns:
        dict with keys: 'status' (str), 'reason' (str), 'checks' (list)
    """
    if resolver is None:
        resolver = dns.resolver.Resolver()
        resolver.timeout = dns_timeout
        resolver.lifetime = dns_timeout + 1.0

    checks_performed = ["syntax"]

    # 1. Query MX records
    try:
        mx_answers = resolver.resolve(domain, "MX")
        checks_performed.append("dns_mx")

        # RFC 7505: Check for Null MX record (priority 0 and target '.')
        # A Null MX indicates the domain explicitly does NOT accept email.
        is_null_mx = False
        valid_mx_targets = []

        for record in mx_answers:
            exchange_str = str(record.exchange).rstrip(".")
            if record.preference == 0 and exchange_str == "":
                is_null_mx = True
                break
            if exchange_str:
                valid_mx_targets.append(exchange_str)

        if is_null_mx:
            return {
                "status": STATUS_LIKELY_BOUNCE,
                "reason": "Domain explicitly rejects all incoming mail (RFC 7505 Null MX configured).",
                "checks_performed": checks_performed,
            }

        if valid_mx_targets:
            return {
                "status": STATUS_LIKELY_DELIVERED,
                "reason": f"Domain has valid mail exchange records ({len(valid_mx_targets)} MX host(s) found).",
                "checks_performed": checks_performed,
            }

    except dns.resolver.NXDOMAIN:
        checks_performed.append("dns_lookup")
        return {
            "status": STATUS_LIKELY_BOUNCE,
            "reason": "Domain does not exist (NXDOMAIN).",
            "checks_performed": checks_performed,
        }
    except (dns.resolver.Timeout, dns.exception.Timeout):
        checks_performed.append("dns_lookup")
        return {
            "status": STATUS_UNKNOWN,
            "reason": "DNS lookup timed out while querying MX records.",
            "checks_performed": checks_performed,
        }
    except (dns.resolver.NoNameservers, dns.resolver.YXDOMAIN):
        checks_performed.append("dns_lookup")
        return {
            "status": STATUS_UNKNOWN,
            "reason": "Temporary DNS resolver failure or nameserver unavailable.",
            "checks_performed": checks_performed,
        }
    except dns.resolver.NoAnswer:
        # Domain exists, but has no MX records. Proceed to fallback check.
        checks_performed.append("dns_mx")
    except Exception as err:
        checks_performed.append("dns_lookup")
        return {
            "status": STATUS_UNKNOWN,
            "reason": f"DNS resolution encountered an error: {type(err).__name__}",
            "checks_performed": checks_performed,
        }

    # 2. RFC 5321 Fallback: Query A and AAAA address records
    has_fallback = False
    try:
        try:
            a_answers = resolver.resolve(domain, "A")
            if len(a_answers) > 0:
                has_fallback = True
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            pass

        if not has_fallback:
            try:
                aaaa_answers = resolver.resolve(domain, "AAAA")
                if len(aaaa_answers) > 0:
                    has_fallback = True
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                pass

        checks_performed.append("dns_fallback_a")

        if has_fallback:
            return {
                "status": STATUS_LIKELY_DELIVERED,
                "reason": "Domain has no MX records, but provides a valid implicit mail route via A/AAAA host records.",
                "checks_performed": checks_performed,
            }
        else:
            return {
                "status": STATUS_LIKELY_BOUNCE,
                "reason": "Domain has no usable mail exchange (MX) or fallback (A/AAAA) host records.",
                "checks_performed": checks_performed,
            }

    except (dns.resolver.Timeout, dns.exception.Timeout):
        checks_performed.append("dns_fallback_a")
        return {
            "status": STATUS_UNKNOWN,
            "reason": "DNS lookup timed out while checking fallback A/AAAA records.",
            "checks_performed": checks_performed,
        }
    except Exception as err:
        checks_performed.append("dns_fallback_a")
        return {
            "status": STATUS_UNKNOWN,
            "reason": f"DNS fallback lookup failed: {type(err).__name__}",
            "checks_performed": checks_performed,
        }


def verify_single_email(
    email: str,
    resolver: Optional[dns.resolver.Resolver] = None,
) -> Dict[str, Any]:
    """Verify an individual email address through syntax and DNS checks."""
    cleaned_input = email.strip() if isinstance(email, str) else ""

    # Step 1: Syntax validation
    syntax_result = validate_syntax(cleaned_input)
    if not syntax_result["valid"]:
        return {
            "email": cleaned_input or "(empty)",
            "status": STATUS_LIKELY_BOUNCE,
            "reason": syntax_result["reason"],
            "checks_performed": ["syntax"],
        }

    domain = syntax_result["domain"]
    normalized_email = syntax_result["normalized"]

    # Step 2: DNS & Mail Route validation
    dns_result = check_domain_dns(domain, resolver=resolver)

    return {
        "email": normalized_email,
        "status": dns_result["status"],
        "reason": dns_result["reason"],
        "checks_performed": dns_result["checks_performed"],
    }


def verify_batch(
    emails: List[str],
    max_batch_size: int = 100,
    resolver: Optional[dns.resolver.Resolver] = None,
) -> Dict[str, Any]:
    """Process a batch of email addresses with duplicate handling and summary counts."""
    if not isinstance(emails, list):
        raise ValueError("The 'emails' field must be a JSON array of strings.")

    total_submitted = len(emails)
    if total_submitted == 0:
        raise ValueError("The 'emails' list cannot be empty. Please provide at least one address.")

    if total_submitted > max_batch_size:
        raise ValueError(
            f"Batch size limit exceeded. Submitted {total_submitted} emails, but the maximum allowed is {max_batch_size}."
        )

    # Clean, normalize, and handle duplicates while preserving submission order
    seen = set()
    unique_emails: List[str] = []
    duplicate_count = 0

    for item in emails:
        if not isinstance(item, str):
            continue
        cleaned = item.strip()
        if not cleaned:
            continue
        lower_key = cleaned.lower()
        if lower_key in seen:
            duplicate_count += 1
            continue
        seen.add(lower_key)
        unique_emails.append(cleaned)

    if not unique_emails:
        raise ValueError("No valid email strings found in the submission.")

    # Shared resolver for DNS query caching across the batch
    if resolver is None:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 3.0
        resolver.lifetime = 4.0

    # Domain cache to avoid redundant DNS lookups for same-domain emails in the batch
    domain_cache: Dict[str, Dict[str, Any]] = {}
    results: List[Dict[str, Any]] = []

    for email_str in unique_emails:
        syntax = validate_syntax(email_str)
        if not syntax["valid"]:
            results.append({
                "email": email_str,
                "status": STATUS_LIKELY_BOUNCE,
                "reason": syntax["reason"],
                "checks_performed": ["syntax"],
            })
            continue

        domain = syntax["domain"]
        normalized = syntax["normalized"]

        if domain in domain_cache:
            dns_res = domain_cache[domain]
        else:
            dns_res = check_domain_dns(domain, resolver=resolver)
            domain_cache[domain] = dns_res

        results.append({
            "email": normalized,
            "status": dns_res["status"],
            "reason": dns_res["reason"],
            "checks_performed": list(dns_res["checks_performed"]),
        })

    # Calculate summary metrics
    likely_delivered_count = sum(1 for r in results if r["status"] == STATUS_LIKELY_DELIVERED)
    likely_bounce_count = sum(1 for r in results if r["status"] == STATUS_LIKELY_BOUNCE)
    unknown_count = sum(1 for r in results if r["status"] == STATUS_UNKNOWN)

    return {
        "results": results,
        "summary": {
            "total_submitted": total_submitted,
            "unique_processed": len(results),
            "duplicates_removed": duplicate_count,
            "likely_delivered": likely_delivered_count,
            "likely_bounce": likely_bounce_count,
            "unknown": unknown_count,
        },
    }
