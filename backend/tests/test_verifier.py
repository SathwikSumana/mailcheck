"""Unit tests for the email verification logic (backend/verifier.py).

All DNS lookups are mocked to ensure 100% deterministic, offline test execution.
"""

from unittest.mock import MagicMock, patch
import pytest
import dns.resolver
import dns.exception

from verifier import (
    STATUS_LIKELY_DELIVERED,
    STATUS_LIKELY_BOUNCE,
    STATUS_UNKNOWN,
    check_domain_dns,
    validate_syntax,
    verify_batch,
    verify_single_email,
)


class TestEmailSyntaxValidation:
    """Tests for Step 1: Email syntax validation."""

    def test_valid_standard_email(self):
        res = validate_syntax("student@example.edu")
        assert res["valid"] is True
        assert res["domain"] == "example.edu"
        assert res["normalized"] == "student@example.edu"

    def test_valid_email_with_dots_and_plus(self):
        res = validate_syntax("john.doe+work@domain.com")
        assert res["valid"] is True
        assert res["domain"] == "domain.com"

    def test_invalid_email_missing_at(self):
        res = validate_syntax("invalidemailaddress.com")
        assert res["valid"] is False
        assert "Missing '@'" in res["reason"]

    def test_invalid_email_missing_local(self):
        res = validate_syntax("@domain.com")
        assert res["valid"] is False
        assert "Missing username" in res["reason"]

    def test_invalid_email_missing_domain(self):
        res = validate_syntax("user@")
        assert res["valid"] is False
        assert "Missing domain" in res["reason"]

    def test_invalid_email_spaces_and_special_chars(self):
        res = validate_syntax("user name@domain .com")
        assert res["valid"] is False

    def test_invalid_email_empty_or_none(self):
        res_empty = validate_syntax("")
        assert res_empty["valid"] is False

        res_none = validate_syntax(None)  # type: ignore
        assert res_none["valid"] is False

    def test_invalid_email_exceeds_max_length(self):
        long_local = "a" * 65
        res = validate_syntax(f"{long_local}@domain.com")
        assert res["valid"] is False
        assert "64 characters" in res["reason"]

    def test_invalid_reserved_tld(self):
        res = validate_syntax("tester@something.invalid")
        assert res["valid"] is False
        assert "reserved" in res["reason"].lower()


class TestDNSAndDomainVerification:
    """Tests for Step 2: DNS & MX records verification (with mocked resolver)."""

    def test_domain_with_valid_mx_records(self):
        mock_resolver = MagicMock()
        mock_record = MagicMock()
        mock_record.preference = 10
        mock_record.exchange = "mail.gooddomain.com."
        mock_resolver.resolve.return_value = [mock_record]

        result = check_domain_dns("gooddomain.com", resolver=mock_resolver)
        assert result["status"] == STATUS_LIKELY_DELIVERED
        assert "valid mail exchange records" in result["reason"]
        assert "dns_mx" in result["checks_performed"]

    def test_domain_with_null_mx_record_rfc7505(self):
        """RFC 7505 Null MX record (preference 0, target '.') explicitly rejects email."""
        mock_resolver = MagicMock()
        mock_record = MagicMock()
        mock_record.preference = 0
        mock_record.exchange = "."
        mock_resolver.resolve.return_value = [mock_record]

        result = check_domain_dns("rejects-mail.com", resolver=mock_resolver)
        assert result["status"] == STATUS_LIKELY_BOUNCE
        assert "Null MX" in result["reason"]
        assert "dns_mx" in result["checks_performed"]

    def test_domain_nonexistent_nxdomain(self):
        mock_resolver = MagicMock()
        mock_resolver.resolve.side_effect = dns.resolver.NXDOMAIN()

        result = check_domain_dns("definitely-does-not-exist-12345.com", resolver=mock_resolver)
        assert result["status"] == STATUS_LIKELY_BOUNCE
        assert "NXDOMAIN" in result["reason"]

    def test_domain_no_mx_but_valid_a_fallback_rfc5321(self):
        """RFC 5321 fallback: no MX records, but domain has A host record."""
        mock_resolver = MagicMock()
        
        def resolve_side_effect(qname, rdtype):
            if rdtype == "MX":
                raise dns.resolver.NoAnswer()
            if rdtype == "A":
                mock_a = MagicMock()
                mock_a.address = "192.0.2.1"
                return [mock_a]
            raise dns.resolver.NoAnswer()

        mock_resolver.resolve.side_effect = resolve_side_effect

        result = check_domain_dns("legacy-server.org", resolver=mock_resolver)
        assert result["status"] == STATUS_LIKELY_DELIVERED
        assert "implicit mail route via A/AAAA" in result["reason"]
        assert "dns_fallback_a" in result["checks_performed"]

    def test_domain_no_mx_and_no_fallback_records(self):
        """Domain exists but has neither MX nor A/AAAA records."""
        mock_resolver = MagicMock()
        mock_resolver.resolve.side_effect = dns.resolver.NoAnswer()

        result = check_domain_dns("dead-route.org", resolver=mock_resolver)
        assert result["status"] == STATUS_LIKELY_BOUNCE
        assert "no usable mail exchange (MX) or fallback" in result["reason"]

    def test_dns_timeout_returns_unknown(self):
        mock_resolver = MagicMock()
        mock_resolver.resolve.side_effect = dns.resolver.Timeout()

        result = check_domain_dns("slow-nameserver.net", resolver=mock_resolver)
        assert result["status"] == STATUS_UNKNOWN
        assert "timed out" in result["reason"]

    def test_dns_temporary_resolver_failure_returns_unknown(self):
        mock_resolver = MagicMock()
        mock_resolver.resolve.side_effect = dns.resolver.NoNameservers()

        result = check_domain_dns("broken-dns.net", resolver=mock_resolver)
        assert result["status"] == STATUS_UNKNOWN
        assert "Temporary DNS resolver failure" in result["reason"]


class TestBatchVerification:
    """Tests for batch processing, deduplication, and limits."""

    def test_batch_verification_with_various_statuses(self):
        mock_resolver = MagicMock()
        
        def mock_resolve(domain, rdtype):
            if domain == "legit.org":
                rec = MagicMock()
                rec.preference = 10
                rec.exchange = "mail.legit.org."
                return [rec]
            elif domain == "nxdomain.com":
                raise dns.resolver.NXDOMAIN()
            elif domain == "timeout.net":
                raise dns.resolver.Timeout()
            raise dns.resolver.NoAnswer()

        mock_resolver.resolve.side_effect = mock_resolve

        emails = [
            "valid.user@legit.org",
            "malformed-email",
            "user@nxdomain.com",
            "contact@timeout.net",
            "valid.user@legit.org",  # duplicate
        ]

        batch_result = verify_batch(emails, resolver=mock_resolver)
        
        results = batch_result["results"]
        summary = batch_result["summary"]

        assert summary["total_submitted"] == 5
        assert summary["unique_processed"] == 4
        assert summary["duplicates_removed"] == 1
        assert summary["likely_delivered"] == 1
        assert summary["likely_bounce"] == 2  # malformed + nxdomain
        assert summary["unknown"] == 1        # timeout

        # Verify results order and contents
        assert results[0]["email"] == "valid.user@legit.org"
        assert results[0]["status"] == STATUS_LIKELY_DELIVERED

        assert results[1]["email"] == "malformed-email"
        assert results[1]["status"] == STATUS_LIKELY_BOUNCE

        assert results[2]["email"] == "user@nxdomain.com"
        assert results[2]["status"] == STATUS_LIKELY_BOUNCE

        assert results[3]["email"] == "contact@timeout.net"
        assert results[3]["status"] == STATUS_UNKNOWN

    def test_empty_batch_raises_value_error(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            verify_batch([])

    def test_oversized_batch_raises_value_error(self):
        oversized = [f"user{i}@test.com" for i in range(101)]
        with pytest.raises(ValueError, match="Batch size limit exceeded"):
            verify_batch(oversized, max_batch_size=100)
