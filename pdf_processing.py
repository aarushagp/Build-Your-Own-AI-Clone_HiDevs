from PyPDF2 import PdfReader

def load_pdf(file_path):
    text = ""

    try:
        print("Opening PDF:", file_path)

        reader = PdfReader(file_path)

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

        print("PDF loaded successfully")

    except Exception as e:
        print("Error reading PDF:", e)

    return text


# test the function
if __name__ == "__main__":
    pdf_file = "ITI_AITechnologyStack.pdf"

    text = load_pdf(pdf_file)

    print("\nFirst 500 characters of PDF:\n")
    print(text[:500])