"""
Form field definitions for Aadhaar Correction and Driving Licence Correction forms.

Each field entry:
  id       - unique key used to store the collected value
  label    - question shown to the user
  page     - 0-indexed PDF page number this field belongs to
  x, y     - position in mm from top-left of page where text is placed
  required - whether the field must be answered (False = optional, can be skipped)

NOTE: Aadhaar form is A4 (210×297 mm). DL form is US Letter (215.9×279.4 mm).
All (x,y) coords were calibrated from rendered PNG grids — do NOT guess.
"""

AADHAAR_FIELDS = [
    # ── Section 2.1: Fields for Correction (Checkboxes) ───────────────────────
    {
        "id": "fields_to_update",
        "label": "Which information do you want to update? (e.g., Name, Address, Mobile, Date of Birth)",
        "page": 0, "x": 60, "y": 72, "required": True,
        "type": "checkbox",
        "options": {
            "Biometric": {"x": 28.5, "y": 72.5},
            "Mobile": {"x": 75.5, "y": 72.5},
            "Date of Birth": {"x": 98.5, "y": 72.5},
            "Address": {"x": 121.5, "y": 72.5},
            "Name": {"x": 141.5, "y": 72.5},
            "Gender": {"x": 160.5, "y": 72.5},
            "Email": {"x": 178.5, "y": 72.5},
        }
    },
    # ── Section 2: Aadhaar Number ─────────────────────────────────────────────
    {
        "id": "aadhaar_number",
        "label": "Your existing 12-digit Aadhaar number (e.g., 1234 5678 9012)",
        "page": 0, "x": 122.2, "y": 62, "required": True,
        "type": "boxed", "box_width": 4.88, "char_count": 12
    },
    # ── Section 3: Full Name ──────────────────────────────────────────────────
    {
        "id": "resident_name",
        "label": "Your full name as it should appear on Aadhaar (e.g., Rohan Sreejith)",
        "page": 0, "x": 60, "y": 78.5, "required": True,
    },
    # ── Section 4: Gender ─────────────────────────────────────────────────────
    {
        "id": "gender",
        "label": "Gender (Male / Female / Transgender)",
        "page": 0, "x": 60, "y": 84, "required": True,
        "type": "checkbox",
        "options": {
            "Male": {"x": 33.5, "y": 85},
            "Female": {"x": 46.5, "y": 85},
            "Transgender": {"x": 61.5, "y": 85}
        }
    },
    # ── Section 5: Date of Birth ──────────────────────────────────────────────
    {
        "id": "dob",
        "label": "Date of birth in DD/MM/YYYY format (e.g., 15/08/1990)",
        "page": 0, "x": 162.5, "y": 84, "required": True,
        "type": "boxed_date"
    },
    # ── Section 6: Address (Two-Column Layout) ────────────────────────────────
    {
        "id": "address_line1",
        "label": "House, Building, or Apartment number (e.g., Flat 101, B-Block)",
        "page": 0, "x": 45, "y": 110, "required": True,
    },
    {
        "id": "address_line2",
        "label": "Street, Road, or Lane name (e.g., MG Road, Baker Street)",
        "page": 0, "x": 125, "y": 110, "required": False,
    },
    {
        "id": "landmark",
        "label": "Nearby landmark (optional - e.g., Near City Hospital)",
        "page": 0, "x": 45, "y": 118, "required": False,
    },
    {
        "id": "area",
        "label": "Area, Locality, or Sector (e.g., Koramangala 4th Block)",
        "page": 0, "x": 125, "y": 118, "required": False,
    },
    {
        "id": "city",
        "label": "Village, Town, or City name (e.g., Trivandrum, Kochi)",
        "page": 0, "x": 45, "y": 124.5, "required": True,
    },
    {
        "id": "post_office",
        "label": "Registered Post Office (e.g., GPO, Pattom SO)",
        "page": 0, "x": 125, "y": 124.5, "required": True,
    },
    {
        "id": "district",
        "label": "District (e.g., Thiruvananthapuram, Ernakulam)",
        "page": 0, "x": 45, "y": 133.5, "required": True,
    },
    {
        "id": "state",
        "label": "State (e.g., Kerala, Tamil Nadu)",
        "page": 0, "x": 125, "y": 133.5, "required": True,
    },
    {
        "id": "email",
        "label": "Email address (e.g., name@example.com)",
        "page": 0, "x": 45, "y": 141, "required": False,
    },
    {
        "id": "mobile",
        "label": "Your 10-digit mobile number (e.g., 9876543210)",
        "page": 0, "x": 118.5, "y": 141, "required": True,
        "type": "boxed", "box_width": 4.88, "char_count": 10
    },
    {
        "id": "pincode",
        "label": "6-digit PIN Code (e.g., 695001)",
        "page": 0, "x": 174.5, "y": 141, "required": True,
        "type": "boxed", "box_width": 4.88, "char_count": 6
    },
    # ── Section 8: Reason for Correction ──────────────────────────────────────
    {
        "id": "correction_reason",
        "label": "Reason for correction (e.g., Spelling mistake in name)",
        "page": 0, "x": 130, "y": 178, "required": True,
    },
    # ── Section 8: Supporting Documents ──────────────────────────────────────
    {
        "id": "documents_enclosed",
        "label": "Documents attached for proof (e.g., Passport, Voter ID, PAN)",
        "page": 0, "x": 45, "y": 168.5, "required": True,
    },
    # ── Section 9: Declaration ────────────────────────────────────────────────
    {
        "id": "place",
        "label": "Place of declaration (e.g., Chennai, Mumbai)",
        "page": 0, "x": 30, "y": 240, "required": True,
    },
    {
        "id": "date",
        "label": "Today's date (DD/MM/YYYY)",
        "page": 0, "x": 160, "y": 240, "required": True,
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# DL Form — US Letter paper (215.9 × 279.4 mm)
# Page 0 = service-type checkboxes + COV  (no personal data here)
# Page 1 = personal details (name, DOB, gender, address, contact)
# Page 2 = pin code continuation + licence particulars + declaration
#
# ALL (x, y) values calibrated from 4× PNG grids (2 mm grid step).
# Table spans x≈42 – x≈183 mm.  Right-column data cells start at x≈93 mm.
# ─────────────────────────────────────────────────────────────────────────────
DL_FIELDS = [
    # ── Page 0: Service Type Checkboxes ──────────────────────────────────────
    # Tick column sits in the right gutter of each service row.
    # x ≈ 183 mm (just inside right edge of the tick box), y varies per row.
    {
        "id": "service_type",
        "label": "What service are you applying for? (e.g. Change of Address, Change of Name, Renewal, Duplicate, Addition of Class)",
        "page": 0, "x": 183, "y": 107, "required": True,
        "type": "checkbox",
        "options": {
            "Learner's Licence":   {"x": 178, "y": 107},
            "New Driving Licence": {"x": 178, "y": 117},
            "Addition of Class":   {"x": 178, "y": 124},
            "Renewal":             {"x": 178, "y": 130},
            "Duplicate":           {"x": 178, "y": 136},
            "Change of Address":   {"x": 178, "y": 143},
            "Change of Name":      {"x": 178, "y": 149},
        },
    },

    # ── Page 1: Aadhaar Card Number (row at y ≈ 97, right cell x ≈ 110) ─────
    {
        "id": "aadhaar_number",
        "label": "Your Aadhaar card number (12 digits, optional — press Enter to skip)",
        "page": 1, "x": 110, "y": 97, "required": False,
    },
    {
        "id": "applicant_name",
        "label": "Full name of the applicant (as it should appear on DL)",
        "page": 1, "x": 44, "y": 118, "required": True,
    },
    # ── Son/wife/daughter of  (full-width row at y ≈ 126) ───────────────────
    {
        "id": "father_husband_name",
        "label": "Father's / Husband's / Wife's full name",
        "page": 1, "x": 44, "y": 124, "required": True,
    },
    # ── Date of birth row (single merged row y ≈ 131) ──────────────────────
    {
        "id": "dob",
        "label": "Date of birth as on DL (DD/MM/YYYY)",
        "page": 1, "x": 44, "y": 131, "required": True,
    },
    # ── Gender checkboxes (y ≈ 138): Male □  Female □  Transgender □ ─────────
    {
        "id": "gender",
        "label": "Gender (Male / Female / Transgender)",
        "page": 1, "x": 44, "y": 138, "required": True,
        "type": "checkbox",
        "options": {
            "Male":        {"x": 30,  "y": 138},
            "Female":      {"x": 44,  "y": 138},
            "Transgender": {"x": 62,  "y": 138},
        },
    },
    # ── Date of Birth box (right half of gender row, x ≈ 156) ────────────────
    {
        "id": "dob_box",
        "label": "Date of Birth (DD/MM/YYYY) — in the Date of Birth box",
        "page": 1, "x": 156, "y": 138, "required": False,
    },
    # ── Educational Qualification (left half of row y ≈ 148) ────────────────
    {
        "id": "educational_qualification",
        "label": "Educational qualification (e.g. 10th Pass, Graduate — press Enter to skip)",
        "page": 1, "x": 44, "y": 148, "required": False,
    },
    # ── Email and Mobile in split row y ≈ 156 ───────────────────────────────
    {
        "id": "email",
        "label": "Email address (optional — press Enter to skip)",
        "page": 1, "x": 44, "y": 156, "required": False,
    },
    {
        "id": "mobile",
        "label": "Mobile number (10 digits)",
        "page": 1, "x": 137, "y": 156, "required": True,
    },

    # ── Section 4 — Present Address ───────────────────────────────────────────
    # Address table: label col x≈43–91, Present col x≈93–136, Permanent x≈136–183
    # We fill the Present column (x=93).
    {
        "id": "address_line1",
        "label": "House / Door / Flat number and Street",
        "page": 1, "x": 93, "y": 200, "required": True,
    },
    {
        "id": "address_line2",
        "label": "Locality / Police Station area / Landmark",
        "page": 1, "x": 93, "y": 209, "required": False,
    },
    {
        "id": "landmark",
        "label": "Landmark (optional — press Enter to skip)",
        "page": 1, "x": 93, "y": 217, "required": False,
    },
    {
        "id": "city",
        "label": "Village / Town / City",
        "page": 1, "x": 93, "y": 223, "required": True,
    },
    {
        "id": "district",
        "label": "District (e.g. Ernakulam, Thiruvananthapuram)",
        "page": 1, "x": 93, "y": 230, "required": True,
    },
    {
        "id": "state",
        "label": "State (e.g. Kerala, Tamil Nadu)",
        "page": 1, "x": 93, "y": 237, "required": True,
    },

    # ── Page 2: PIN code (top of page 2, Present address continued) ─────────
    {
        "id": "pincode",
        "label": "PIN Code (6 digits)",
        "page": 2, "x": 93, "y": 45, "required": True,
    },
    # ── Section 6 — Existing Licence Particulars ──────────────────────────────
    {
        "id": "dl_number",
        "label": "Existing Driving Licence number (e.g. KL01-20200012345)",
        "page": 2, "x": 93, "y": 130, "required": True,
    },
    {
        "id": "vehicle_class",
        "label": "Vehicle class(es) on your existing DL (e.g. LMV, MCWG, Transport)",
        "page": 2, "x": 93, "y": 141, "required": True,
    },
    {
        "id": "rto_name",
        "label": "Name of the Licencing Authority (RTO) that issued your DL",
        "page": 2, "x": 93, "y": 150, "required": True,
    },
    {
        "id": "dl_validity_from",
        "label": "DL validity FROM date (DD/MM/YYYY)",
        "page": 2, "x": 93, "y": 160, "required": True,
    },
    {
        "id": "dl_validity_to",
        "label": "DL validity TO date (DD/MM/YYYY)",
        "page": 2, "x": 148, "y": 160, "required": True,
    },
    # ── Declaration — Date (y ≈ 196) ────────────────────────────────────────
    {
        "id": "date",
        "label": "Today's date (DD/MM/YYYY)",
        "page": 2, "x": 50, "y": 196, "required": True,
    },
]

FORM_FIELDS = {
    "aadhaar": AADHAAR_FIELDS,
    "dl": DL_FIELDS,
}

FORM_LABELS = {
    "aadhaar": "Aadhaar Correction Form",
    "dl": "Driving Licence Correction Form",
}

POST_SUBMISSION_INSTRUCTIONS = {
    "aadhaar": (
        "**What to do with your filled Aadhaar Correction Form:**\n"
        "1. Print the form on A4 paper.\n"
        "2. Affix a recent passport-size photograph in the given space.\n"
        "3. Attach self-attested copies of: Proof of Identity (POI), Proof of Address (POA), and Proof of Date of Birth (POB) if applicable.\n"
        "4. Sign the form in the designated signature box.\n"
        "5. Visit your nearest **Aadhaar Enrolment/Update Centre** (book a slot free at appointments.uidai.gov.in).\n"
        "6. Submit the form along with originals of supporting documents for verification.\n"
        "7. **The correction service is completely FREE of charge.** Insist on a receipt/acknowledgement slip.\n"
        "8. Track correction status at: https://myaadhaar.uidai.gov.in"
    ),
    "dl": (
        "**What to do with your filled Driving Licence Correction Form:**\n"
        "1. Print the form on A4 paper.\n"
        "2. Attach: self-attested copy of existing DL, one recent passport-size photo, address proof (Aadhaar/Passport/Voter ID).\n"
        "3. Sign the declaration section of the form.\n"
        "4. Take the form + documents to your **issuing RTO (Regional Transport Office)**.\n"
        "5. Pay the applicable fee (usually ₹200–₹500 depending on your state).\n"
        "6. Collect the acknowledgement receipt — you may need it to track the corrected DL delivery.\n"
        "7. Alternatively, many states allow DL corrections via the **Sarathi Parivahan portal**: https://sarathi.parivahan.gov.in"
    ),
}
