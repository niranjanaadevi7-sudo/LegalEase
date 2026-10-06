import os
import asyncio
from pathlib import Path

from dotenv import load_dotenv

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel

from google import genai


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ============================================================
# GEMINI CLIENT
# ============================================================

client = None

if GEMINI_API_KEY:
    client = genai.Client(
        api_key=GEMINI_API_KEY
    )


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="LegalEase",
    description="AI-powered legal document assistant",
    version="1.0.0"
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

TEMPLATES_DIR = BASE_DIR / "templates"

STATIC_DIR = BASE_DIR / "static"


# ============================================================
# STATIC FILES
# ============================================================

app.mount(
    "/static",
    StaticFiles(
        directory=STATIC_DIR
    ),
    name="static"
)


# ============================================================
# TEMPLATES
# ============================================================

templates = Jinja2Templates(
    directory=TEMPLATES_DIR
)


# ============================================================
# REQUEST MODEL
# ============================================================

class DocumentRequest(BaseModel):

    document_type: str

    purpose: str = ""

    description: str


# ============================================================
# HOME PAGE
# ============================================================

@app.get(
    "/",
    response_class=HTMLResponse
)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():

    return {
        "status": "online",
        "application": "LegalEase"
    }


# ============================================================
# GEMINI TEST
# ============================================================

@app.get("/test-ai")
async def test_ai():

    if client is None:

        return {
            "success": False,
            "message": (
                "Gemini API key is not configured."
            )
        }

    try:

        response = client.models.generate_content(

            model="gemini-3.8-flash",

            contents=(
                "Say hello from LegalEase "
                "in one short sentence."
            )
        )

        return {

            "success": True,

            "response": response.text

        }

    except Exception as error:

        return {

            "success": False,

            "error": str(error)

        }


# ============================================================
# GENERATE LEGAL DOCUMENT
# ============================================================

@app.post("/generate")
async def generate_document(
    data: DocumentRequest
):

    # --------------------------------------------------------
    # CHECK API KEY
    # --------------------------------------------------------

    if client is None:

        raise HTTPException(

            status_code=500,

            detail=(
                "Gemini API key is not configured. "
                "Please check your .env file."
            )

        )


    # --------------------------------------------------------
    # VALIDATE DOCUMENT TYPE
    # --------------------------------------------------------

    if not data.document_type.strip():

        raise HTTPException(

            status_code=400,

            detail=(
                "Please select a document type."
            )

        )


    # --------------------------------------------------------
    # VALIDATE DESCRIPTION
    # --------------------------------------------------------

    if not data.description.strip():

        raise HTTPException(

            status_code=400,

            detail=(
                "Please describe what "
                "document you need."
            )

        )


    # --------------------------------------------------------
    # CREATE PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are LegalEase, an AI-powered legal
document drafting assistant.

Your task is to create a professional
DRAFT legal document based on the
information provided by the user.

DOCUMENT TYPE:
{data.document_type}

PURPOSE:
{data.purpose}

USER REQUIREMENTS:
{data.description}

IMPORTANT INSTRUCTIONS:

1. Create a clear and professional
   legal document draft.

2. Use appropriate headings,
   sections and clauses.

3. Use placeholders when information
   is missing.

Examples:

[PARTY NAME]
[ADDRESS]
[DATE]
[AMOUNT]
[COMPANY NAME]

4. Never invent personal information.

5. Make the document easy to read.

6. Include appropriate sections such as:

   - Parties
   - Purpose
   - Responsibilities
   - Terms and Conditions
   - Payment, if relevant
   - Confidentiality, if relevant
   - Termination, if relevant
   - Dispute Resolution, if relevant
   - Signatures

7. Adapt the clauses to the selected
   document type.

8. At the end include:

IMPORTANT NOTICE:
This document is an AI-generated
draft for informational purposes.
It is not legal advice and should
be reviewed by a qualified legal
professional before use.

9. Do not claim that the document is
   legally valid in a particular
   jurisdiction.

Return ONLY the document draft.
"""


    # --------------------------------------------------------
    # CALL GEMINI WITH RETRY
    # --------------------------------------------------------

    response = None

    for attempt in range(3):

        try:

            print(
                f"Gemini request attempt "
                f"{attempt + 1}/3"
            )

            response = client.models.generate_content(

                model="gemini-3.8-flash",

                contents=prompt

            )

            break


        except Exception as error:

            error_text = str(error)

            print(
                f"Gemini attempt "
                f"{attempt + 1} failed:"
            )

            print(error_text)


            # ------------------------------------------------
            # RETRY TEMPORARY 503 ERROR
            # ------------------------------------------------

            if (
                "503" in error_text
                or
                "UNAVAILABLE" in error_text
            ):

                if attempt < 2:

                    print(
                        "Gemini is temporarily "
                        "unavailable."
                    )

                    print(
                        "Retrying in 3 seconds..."
                    )

                    await asyncio.sleep(3)

                    continue


            # ------------------------------------------------
            # OTHER ERRORS
            # ------------------------------------------------

            raise


    # --------------------------------------------------------
    # CHECK RESPONSE
    # --------------------------------------------------------

    if response is None:

        raise HTTPException(

            status_code=503,

            detail=(
                "Gemini is temporarily unavailable. "
                "Please try again."
            )

        )


    if not response.text:

        raise HTTPException(

            status_code=500,

            detail=(
                "Gemini returned an empty response."
            )

        )


    # --------------------------------------------------------
    # RETURN GENERATED DOCUMENT
    # --------------------------------------------------------

    return {

        "success": True,

        "document": response.text

    }


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        "main:app",

        host="127.0.0.1",

        port=8000,

        reload=True

    )