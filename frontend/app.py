import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
import html
import os

import requests
import streamlit as st

from dotenv import load_dotenv

from backend.services.document_formatter import (
    format_docx,
    format_pdf,
)

from backend.services.text_utils import (
    plain_text_bytes,
    terms_from_text,
)


load_dotenv()


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)


# -----------------------------
# Custom CSS
# -----------------------------

st.markdown(
    """
    <style>

    .hero {
        padding: 1.5rem;
        border-radius: 14px;
        background: linear-gradient(
            135deg,
            #111827,
            #263449
        );
        color: white;
        margin-bottom: 1rem;
    }

    .hero h1 {
        margin-bottom: 0.3rem;
    }

    .hero p {
        margin: 0;
    }

    .preview {
        background: #111827;
        color: #f3f4f6;
        border-radius: 12px;
        padding: 1.2rem;
        max-height: 650px;
        overflow-y: auto;
        white-space: pre-wrap;
        font-family: Georgia, serif;
        line-height: 1.55;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Header
# -----------------------------

st.markdown(
    """
    <div class="hero">

        <h1>⚖️ LegalEase</h1>

        <p>
            AI-assisted legal document drafting,
            editing and export.
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


st.info(
    "AI-generated drafts are not legal advice. "
    "Review the final document with a qualified "
    "legal professional before signing or relying on it."
)


# -----------------------------
# Session State
# -----------------------------

if "document" not in st.session_state:

    st.session_state.document = ""


if "model" not in st.session_state:

    st.session_state.model = ""


# -----------------------------
# Sidebar
# -----------------------------

with st.sidebar:

    st.header(
        "Document Details"
    )

    document_type = st.selectbox(
        "Document Type",

        [
            "Employment Contract",
            "Non-Disclosure Agreement",
            "Lease Agreement",
            "Employment Offer Letter",
            "Freelance Work Contract",
            "General Agreement",
            "Other",
        ],
    )

    if document_type == "Other":

        document_type = st.text_input(
            "Custom Document Type"
        )

    parties = st.text_area(
        "Parties",

        placeholder=(
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),

        height=110,
    )

    terms_text = st.text_area(
        "Terms & Conditions",

        placeholder=(
            "Payment within 30 days of invoice; "
            "Confidentiality must be maintained; "
            "Either party may terminate with 15 days notice"
        ),

        height=170,
    )

    dates = st.text_input(
        "Effective Date",

        placeholder=(
            "September 28, 2026"
        ),
    )

    jurisdiction = st.text_input(
        "Jurisdiction",

        placeholder="India",
    )

    logo_file = st.file_uploader(
        "Logo (Optional)",

        type=[
            "png",
            "jpg",
            "jpeg",
        ],
    )

    generate = st.button(
        "Generate Document",

        type="primary",

        use_container_width=True,
    )


# -----------------------------
# Generate Document
# -----------------------------

if generate:

    terms = terms_from_text(
        terms_text
    )

    missing = []

    if not document_type.strip():

        missing.append(
            "document type"
        )

    if not parties.strip():

        missing.append(
            "parties"
        )

    if not terms:

        missing.append(
            "at least one term"
        )

    if not dates.strip():

        missing.append(
            "effective date"
        )

    if missing:

        st.error(
            "Please provide: "
            + ", ".join(missing)
            + "."
        )

    else:

        payload = {

            "document_type":
                document_type.strip(),

            "parties":
                parties.strip(),

            "terms":
                terms,

            "dates":
                dates.strip(),

            "jurisdiction":
                jurisdiction.strip()
                or None,
        }

        with st.spinner(
            "Generating your document..."
        ):

            try:

                response = requests.post(

                    f"{BACKEND_URL}/generate",

                    json=payload,

                    timeout=120,
                )

                if response.ok:

                    data = response.json()

                    st.session_state.document = (
                        data["content"]
                    )

                    st.session_state.model = (
                        data.get(
                            "model",
                            "",
                        )
                    )

                    st.success(
                        "Document generated successfully."
                    )

                else:

                    try:

                        detail = response.json().get(
                            "detail",
                            response.text,
                        )

                    except Exception:

                        detail = response.text

                    st.error(
                        f"Backend error "
                        f"({response.status_code}): "
                        f"{detail}"
                    )

            except requests.RequestException as exc:

                st.error(
                    "Could not connect to FastAPI. "
                    "Make sure the backend is running.\n\n"
                    f"Details: {exc}"
                )


# -----------------------------
# Document Preview
# -----------------------------

st.subheader(
    "Document Preview"
)


if st.session_state.document:

    edited = st.text_area(

        "Edit the Generated Document",

        value=st.session_state.document,

        height=550,
    )

    st.session_state.document = edited


    # HTML preview

    preview = (
        html.escape(
            edited
        )
        .replace(
            "\n",
            "<br>"
        )
    )


    st.markdown(
        f"""
        <div class="preview">
            {preview}
        </div>
        """,

        unsafe_allow_html=True,
    )


    # -----------------------------
    # Download
    # -----------------------------

    terms = terms_from_text(
        terms_text
    )


    logo_bytes = (
        logo_file.getvalue()
        if logo_file
        else None
    )


    col1, col2, col3 = st.columns(
        3
    )


    # TXT

    with col1:

        txt_data = plain_text_bytes(
            edited
        )

        st.download_button(

            "Download TXT",

            data=txt_data,

            file_name=(
                "legalease_document.txt"
            ),

            mime="text/plain",

            use_container_width=True,
        )


    # DOCX

    with col2:

        docx_data = format_docx(

            edited,

            document_type,

            terms=terms,

            logo_bytes=logo_bytes,
        )

        st.download_button(

            "Download DOCX",

            data=docx_data,

            file_name=(
                "legalease_document.docx"
            ),

            mime=(
                "application/vnd.openxmlformats-"
                "officedocument.wordprocessingml.document"
            ),

            use_container_width=True,
        )


    # PDF

    with col3:

        pdf_data = format_pdf(

            edited,

            document_type,

            logo_bytes=logo_bytes,
        )

        st.download_button(

            "Download PDF",

            data=pdf_data,

            file_name=(
                "legalease_document.pdf"
            ),

            mime="application/pdf",

            use_container_width=True,
        )


    st.caption(
        "Gemini model: "
        + (
            st.session_state.model
            or "Configured model"
        )
    )


else:

    st.write(
        "Enter the document details "
        "in the sidebar and click "
        "**Generate Document**."
    )