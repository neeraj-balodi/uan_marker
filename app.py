import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import os

def highlight_uan_numbers(pdf_path, excel_path, output_path):
    df = pd.read_excel(excel_path)
    uan_numbers = df["UAN No."].dropna().astype(int).astype(str).tolist()

    pdf_document = fitz.open(pdf_path)

    pages_to_keep = [0]  

    for page_number in range(1, len(pdf_document)):
        page = pdf_document.load_page(page_number)
        page_text = page.get_text()

        contains_uan = False
        for uan in uan_numbers:
            if uan in page_text:
                contains_uan = True
                # Highlight the UAN number
                text_instances = page.search_for(uan)
                for inst in text_instances:
                    highlight = page.add_highlight_annot(inst)
                    highlight.update()

        if contains_uan:
            pages_to_keep.append(page_number)

    new_pdf = fitz.open()
    for page_number in pages_to_keep:
        new_pdf.insert_pdf(pdf_document, from_page=page_number, to_page=page_number)

    new_pdf.save(output_path)
    new_pdf.close()
    pdf_document.close()

st.title("UAN Marker")
st.write("Upload a PDF file and an Excel file with UAN numbers to highlight the UAN numbers in the PDF.")

pdf_file = st.file_uploader("Upload PDF File", type=["pdf"])
excel_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if pdf_file and excel_file:
    pdf_path = pdf_file.name
    excel_path = excel_file.name

    with open(pdf_path, "wb") as f:
        f.write(pdf_file.getbuffer())

    with open(excel_path, "wb") as f:
        f.write(excel_file.getbuffer())

    output_filename = os.path.splitext(excel_path)[0] + '.pdf'
    output_path = os.path.join(os.path.dirname(excel_path), output_filename)

    highlight_uan_numbers(pdf_path, excel_path, output_path)

    with open(output_path, "rb") as f:
        st.download_button("Download Processed PDF", f, file_name=output_filename)

    st.success(f"Processed PDF saved as: {output_filename}")
    
