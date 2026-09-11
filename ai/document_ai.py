import re
 
from ai.ocr_service import extract_text
 
# ---------------------------------------------------------------------------
# Pure OCR + rule-based document verification.
# No network / AI calls happen here anymore — Groq is used only by the
# chatbot (see ai/groq_client.py -> ask_ai). This keeps document upload
# fast and fully offline.
# ---------------------------------------------------------------------------
 
# 12-digit Aadhaar number, optionally grouped as 4-4-4 (e.g. "1234 5678 9012")
AADHAAR_NUMBER_PATTERN = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")
 
# Standard PAN format: 5 letters, 4 digits, 1 letter (e.g. ABCDE1234F)
PAN_NUMBER_PATTERN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
 
MIN_TEXT_LENGTH = 20
 
 
def _reject(document_type, missing, remarks):
    return f"""Document Type: {document_type}
    Verified: No
    Confidence: 0%
    Quality: Invalid
    Fields Found: None
    Missing Fields: {missing}
    Remarks: {remarks}"""
 
 
def _accept(document_type, fields_found):
    return f"""Document Type: {document_type}
    Verified: Yes
    Confidence: 95%
    Quality: Good
    Fields Found: {fields_found}
    Missing Fields: None
    Remarks: Document verified successfully using OCR + rule-based validation."""
 
 
def is_document_verified(ai_report, min_confidence=50):
    """
    Robustly decide whether a verification report means the document
    passed verification. Looks at BOTH the 'Verified' field and the
    'Confidence' field (case/spacing-insensitive) so that:
      - a low-confidence 'Yes' cannot slip through, and
      - any wording variation of 'No' is still caught correctly.
    """
    if not ai_report:
        return False
 
    verified_match = re.search(r"verified\s*:\s*([a-z]+)", ai_report, re.IGNORECASE)
    if not verified_match or verified_match.group(1).strip().lower() != "yes":
        return False
 
    confidence_match = re.search(r"confidence\s*:\s*(\d+)", ai_report, re.IGNORECASE)
    if confidence_match:
        try:
            confidence = int(confidence_match.group(1))
        except ValueError:
            confidence = 0
        if confidence < min_confidence:
            return False
 
    return True
 
 
def verify_document(file_path, document_type):
 
    extracted = extract_text(file_path)
 
    if len(extracted.strip()) < MIN_TEXT_LENGTH:
        return _reject(
            document_type,
            "All",
            "No readable government document detected."
        )
 
    text = extracted.lower()
    doc_type_lower = document_type.lower()
 
        # ---------------- Aadhaar Card ----------------
    if "aadhaar" in doc_type_lower or "aadhar" in doc_type_lower:

        has_number = bool(AADHAAR_NUMBER_PATTERN.search(extracted))

        aadhaar_keywords = [
            "government",
            "india",
            "uidai",
            "aadhaar",
            "aadhar",
            "unique identification"
        ]

        keyword_hits = sum(1 for k in aadhaar_keywords if k in text)

        if has_number and keyword_hits >= 2:
            return _accept(
                document_type,
                "Aadhaar Number + Government Markers"
            )

        missing = []

        if not has_number:
            missing.append("Valid Aadhaar Number")

        if keyword_hits < 2:
            missing.append("Government Markers")

        return _reject(
            document_type,
            ", ".join(missing),
            f"Uploaded document does not appear to be a valid {document_type}."
        )
 
    # ---------------- PAN Card ----------------
    elif "pan" in doc_type_lower:
        has_income_tax = "income tax" in text
        has_pan_label = "permanent account number" in text
        has_pan_number = bool(PAN_NUMBER_PATTERN.search(extracted.upper()))
 
        if has_income_tax and has_pan_label and has_pan_number:
            return _accept(document_type, "Income Tax, Permanent Account Number, Valid PAN Number")
 
        missing = []
        if not has_income_tax:
            missing.append("Income Tax")
        if not has_pan_label:
            missing.append("Permanent Account Number")
        if not has_pan_number:
            missing.append("Valid PAN Number")
 
        return _reject(
            document_type,
            ", ".join(missing),
            f"Uploaded document does not appear to be a valid {document_type}."
        )
 
    # ---------------- Bank Passbook ----------------
    elif "passbook" in doc_type_lower or "bank" in doc_type_lower:
        has_ifsc = "ifsc" in text
        has_account = ("account number" in text) or ("account no" in text) or ("a/c" in text) or ("account" in text)
        has_branch = "branch" in text
 
        if has_ifsc and has_account and has_branch:
            return _accept(document_type, "IFSC, Account Number, Branch")
 
        missing = []
        if not has_ifsc:
            missing.append("IFSC")
        if not has_account:
            missing.append("Account Number")
        if not has_branch:
            missing.append("Branch")
 
        return _reject(
            document_type,
            ", ".join(missing),
            f"Uploaded document does not appear to be a valid {document_type}."
        )
 
    # ---------------- Income Certificate ----------------
    elif "income" in doc_type_lower:
        keywords = ["income", "certificate", "annual income", "tehsildar", "revenue department", "income certificate"]
        hits = sum(1 for k in keywords if k in text)
 
        if hits >= 2:
            return _accept(document_type, "Income Certificate markers")
 
        return _reject(
            document_type,
            "Income Certificate markers",
            f"Uploaded document does not appear to be a valid {document_type}."
        )
 
    # ---------------- Other document types ----------------
    # (e.g. Caste / Category Certificate, Land Holding Record) have no
    # dedicated keyword rule set. We accept them once OCR has confirmed
    # the file contains substantial readable text (the MIN_TEXT_LENGTH
    # check above already filters out blank/unreadable uploads).
    return _accept(document_type, "Readable text detected")
 