"""Boundary tests without a live ERPNext server or real CAPTCHA credentials."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock

frappe = types.ModuleType("frappe")
frappe.whitelist = lambda **kw: lambda fn: fn
limiter = types.ModuleType("frappe.rate_limiter")
limiter.rate_limit = lambda **kw: lambda fn: fn
requests = types.ModuleType("requests")
requests.RequestException = type("RequestException", (Exception,), {})
sys.modules.update({"frappe": frappe, "frappe.rate_limiter": limiter, "requests": requests})
spec = importlib.util.spec_from_file_location("website_leads", Path(__file__).with_name("website_leads.py"))
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)


class LeadBoundaryTests(unittest.TestCase):
    def setUp(self):
        frappe.local = types.SimpleNamespace(response={})
        frappe.request = types.SimpleNamespace(content_length=1000)
        frappe.conf = {"e2e_recaptcha_secret": "test-secret-not-a-real-key"}
        frappe.get_request_header = Mock(return_value="https://e2erecycling.com")
        frappe.get_doc = Mock()
        frappe.db = Mock()
        frappe.logger = Mock()
        requests.post = Mock()
        requests.post.return_value.json.return_value = {"success": True, "hostname": "e2erecycling.com"}
        self.payload = dict(contact_name="Integration Test", company="Example Company", work_email="it@example.com",
                            phone="+91 9000000000", city_locations="Bengaluru", asset_types_volume="20 laptops",
                            requirement_details="Data wiping and collection", recaptcha_response="test-token-" * 10, website="")

    def rejected(self, code):
        self.assertEqual(api.submit(**self.payload)["code"], code)
        frappe.get_doc.assert_not_called()

    def test_success_maps_only_fixed_doctype_fields(self):
        self.assertTrue(api.submit(**self.payload)["ok"])
        doc = frappe.get_doc.call_args.args[0]
        self.assertEqual(doc["doctype"], "e2e Website Leads")
        self.assertEqual(doc["citylocation"], "Bengaluru")
        self.assertEqual(doc["asset_typesapproximate_volume"], "20 laptops")
        self.assertNotIn("recaptcha_response", doc)
        frappe.get_doc.return_value.insert.assert_called_once_with(ignore_permissions=True)

    def test_wrong_origin(self):
        frappe.get_request_header.return_value = "https://evil.example"
        self.rejected("origin")

    def test_mass_assignment(self):
        self.payload["doctype"] = "User"
        self.rejected("fields")

    def test_honeypot(self):
        self.payload["website"] = "spam"
        self.rejected("verification")

    def test_required_and_length_validation(self):
        for field in api.FIELDS:
            original = self.payload[field]
            for invalid in (None, " ", ["value"], "x" * (api.FIELDS[field][1] + 1)):
                self.payload[field] = invalid
                self.rejected("validation")
            self.payload[field] = original

    def test_html_email_and_phone_validation(self):
        for field, value in (("company", "<script>alert(1)</script>"), ("work_email", "bad-email"), ("phone", "invalid")):
            original = self.payload[field]
            self.payload[field] = value
            self.rejected("validation")
            self.payload[field] = original

    def test_missing_captcha(self):
        self.payload["recaptcha_response"] = ""
        self.rejected("captcha")

    def test_missing_configuration(self):
        frappe.conf = {}
        self.rejected("unavailable")
        requests.post.assert_not_called()

    def test_failed_captcha_and_wrong_hostname(self):
        for response in ({"success": False}, {"success": True, "hostname": "elsewhere.example"}, {"success": "true", "hostname": "e2erecycling.com"}):
            requests.post.return_value.json.return_value = response
            self.rejected("captcha")

    def test_verification_network_failure(self):
        requests.post.side_effect = requests.RequestException("secret must never be returned")
        result = api.submit(**self.payload)
        self.assertEqual(result["code"], "unavailable")
        self.assertNotIn("secret", result["message"])
        frappe.get_doc.assert_not_called()

    def test_database_failure_rolls_back(self):
        frappe.get_doc.return_value.insert.side_effect = RuntimeError("private database information")
        result = api.submit(**self.payload)
        self.assertEqual(result["code"], "unavailable")
        self.assertNotIn("private", result["message"])
        frappe.db.rollback.assert_called_once()

    def test_request_limit(self):
        frappe.request.content_length = 24001
        self.rejected("size")


if __name__ == "__main__":
    unittest.main()
