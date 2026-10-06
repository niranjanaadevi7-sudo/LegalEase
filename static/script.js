// ============================================================
// LEGAL EASE - FRONTEND LOGIC
// ============================================================


// ------------------------------------------------------------
// ELEMENTS
// ------------------------------------------------------------

const documentType =
    document.getElementById("documentType");

const purpose =
    document.getElementById("purpose");

const description =
    document.getElementById("description");

const generateBtn =
    document.getElementById("generateBtn");

const resultCard =
    document.getElementById("resultCard");

const result =
    document.getElementById("result");

const resultTitle =
    document.getElementById("resultTitle");

const counter =
    document.getElementById("counter");

const copyBtn =
    document.getElementById("copyBtn");

const downloadTxt =
    document.getElementById("downloadTxt");


// ------------------------------------------------------------
// CHARACTER COUNTER
// ------------------------------------------------------------

description.addEventListener(
    "input",
    function () {

        counter.textContent =
            `${description.value.length} characters`;

    }
);


// ------------------------------------------------------------
// GENERATE DOCUMENT
// ------------------------------------------------------------

generateBtn.addEventListener(
    "click",
    generateDocument
);


async function generateDocument() {

    // Get values

    const type =
        documentType.value.trim();

    const userPurpose =
        purpose.value.trim();

    const userDescription =
        description.value.trim();


    // --------------------------------------------------------
    // VALIDATION
    // --------------------------------------------------------

    if (!type) {

        alert(
            "Please select a document type."
        );

        documentType.focus();

        return;

    }


    if (!userDescription) {

        alert(
            "Please describe what you need."
        );

        description.focus();

        return;

    }


    // --------------------------------------------------------
    // LOADING STATE
    // --------------------------------------------------------

    generateBtn.disabled = true;

    generateBtn.innerHTML =
        "⏳ Generating your document...";


    resultCard.classList.add(
        "hidden"
    );


    // --------------------------------------------------------
    // REQUEST DATA
    // --------------------------------------------------------

    const requestData = {

        document_type: type,

        purpose: userPurpose,

        description: userDescription

    };


    try {

        // ----------------------------------------------------
        // SEND REQUEST TO FASTAPI
        // ----------------------------------------------------

        const response =
            await fetch(
                "/generate",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            requestData
                        )

                }
            );


        // ----------------------------------------------------
        // READ RESPONSE
        // ----------------------------------------------------

        const data =
            await response.json();


        // ----------------------------------------------------
        // HANDLE SERVER ERROR
        // ----------------------------------------------------

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Something went wrong."
            );

        }


        // ----------------------------------------------------
        // DISPLAY RESULT
        // ----------------------------------------------------

        resultTitle.textContent =
            type;

        result.textContent =
            data.document;

        resultCard.classList.remove(
            "hidden"
        );


        // Scroll to generated document

        resultCard.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });


    } catch (error) {

        console.error(
            "LegalEase Error:",
            error
        );


        alert(
            "Unable to generate the document.\n\n"
            + error.message
        );


    } finally {

        // ----------------------------------------------------
        // RESET BUTTON
        // ----------------------------------------------------

        generateBtn.disabled = false;

        generateBtn.innerHTML =
            "<span>✨</span> Generate Document";

    }

}


// ------------------------------------------------------------
// COPY DOCUMENT
// ------------------------------------------------------------

copyBtn.addEventListener(
    "click",
    async function () {

        const text =
            result.textContent.trim();


        if (!text) {

            alert(
                "There is no document to copy."
            );

            return;

        }


        try {

            await navigator.clipboard.writeText(
                text
            );

            copyBtn.textContent =
                "Copied ✓";


            setTimeout(
                function () {

                    copyBtn.textContent =
                        "Copy";

                },
                2000
            );


        } catch (error) {

            console.error(error);

            alert(
                "Unable to copy the document."
            );

        }

    }
);


// ------------------------------------------------------------
// DOWNLOAD TEXT FILE
// ------------------------------------------------------------

downloadTxt.addEventListener(
    "click",
    function () {

        const text =
            result.textContent.trim();


        if (!text) {

            alert(
                "There is no document to download."
            );

            return;

        }


        const blob =
            new Blob(
                [text],
                {
                    type: "text/plain"
                }
            );


        const url =
            URL.createObjectURL(
                blob
            );


        const link =
            document.createElement("a");


        link.href = url;

        link.download =
            "LegalEase_Document.txt";


        document.body.appendChild(
            link
        );


        link.click();


        link.remove();


        URL.revokeObjectURL(
            url
        );

    }
);


// ------------------------------------------------------------
// SIDEBAR NAVIGATION
// ------------------------------------------------------------

const navButtons =
    document.querySelectorAll(
        ".nav-btn"
    );


navButtons.forEach(
    function (button) {

        button.addEventListener(
            "click",
            function () {

                navButtons.forEach(
                    function (item) {

                        item.classList.remove(
                            "active"
                        );

                    }
                );


                button.classList.add(
                    "active"
                );


                const text =
                    button.textContent.trim();


                if (
                    text.includes(
                        "Dashboard"
                    )
                ) {

                    window.scrollTo({
                        top: 0,
                        behavior: "smooth"
                    });

                }


                if (
                    text.includes(
                        "Documents"
                    )
                ) {

                    alert(
                        "Document history will be added in the next version."
                    );

                }


                if (
                    text.includes(
                        "AI Assistant"
                    )
                ) {

                    alert(
                        "AI Assistant is powered by Gemini."
                    );

                }


                if (
                    text.includes(
                        "About"
                    )
                ) {

                    alert(
                        "LegalEase is an AI-powered legal document drafting assistant."
                    );

                }

            }
        );

    }
);