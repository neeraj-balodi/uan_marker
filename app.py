import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import os
from tempfile import NamedTemporaryFile

def highlight_numbers(pdf_path, numbers, output_path, number_type):
    pdf_document = fitz.open(pdf_path)

    pages_to_keep = [0]
    total_matches = 0

    for page_number in range(1, len(pdf_document)):
        page = pdf_document.load_page(page_number)
        page_text = page.get_text()

        contains_number = False
        page_matches = 0
        for number in numbers:
            matches = page.search_for(number)
            if matches:
                contains_number = True
                page_matches += len(matches)
                for match in matches:
                    highlight = page.add_highlight_annot(match)
                    highlight.update()

        if contains_number:
            pages_to_keep.append(page_number)

        total_matches += page_matches

    st.write(f"Total {number_type} matches found: {total_matches}")

    new_pdf = fitz.open()
    for page_number in pages_to_keep:
        new_pdf.insert_pdf(pdf_document, from_page=page_number, to_page=page_number)

    new_pdf.save(output_path)
    new_pdf.close()
    pdf_document.close()

st.title("UAN & ESIC Number Marker")

uan_pdf_file = st.file_uploader("Upload PF PDF File", type=["pdf"])
esic_pdf_file = st.file_uploader("Upload ESIC PDF File", type=["pdf"])
excel_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uan_pdf_file and esic_pdf_file and excel_file:
    with NamedTemporaryFile(delete=False, suffix=".pdf") as uan_pdf_temp, NamedTemporaryFile(delete=False, suffix=".pdf") as esic_pdf_temp, NamedTemporaryFile(delete=False, suffix=".xlsx") as excel_temp:
        uan_pdf_temp.write(uan_pdf_file.getbuffer())
        esic_pdf_temp.write(esic_pdf_file.getbuffer())
        excel_temp.write(excel_file.getbuffer())
        uan_pdf_temp_path = uan_pdf_temp.name
        esic_pdf_temp_path = esic_pdf_temp.name
        excel_temp_path = excel_temp.name

    # Get the first 3 characters of the Excel file name
    excel_basename = os.path.basename(excel_file.name)
    base_name = excel_basename[:3]

    output_uan_path = os.path.join(os.path.dirname(uan_pdf_temp_path), f"{base_name}_PF_highlighted.pdf")
    output_esic_path = os.path.join(os.path.dirname(esic_pdf_temp_path), f"{base_name}_ESIC_highlighted.pdf")

    df = pd.read_excel(excel_temp_path, skiprows=6)
    
    st.write("Columns in the Excel file:", df.columns.tolist())
    
    # Ensure correct column names
    uan_column = "UAN No."
    esic_column = "ESI No"
    if uan_column not in df.columns or esic_column not in df.columns:
        st.error(f"Columns '{uan_column}' or '{esic_column}' not found in the Excel file.")
        raise Exception(f"Columns '{uan_column}' or '{esic_column}' not found in the Excel file.")
    
    # Filter and process UAN numbers
    df = df[df[uan_column].notna() & (df[uan_column] != "EXEMPTED")]
    df[uan_column] = df[uan_column].astype(float).astype(int).astype(str).str.strip()
    uan_numbers = df[uan_column].tolist()
    st.write("Processed UAN Numbers:", uan_numbers)  # Debugging line

    # Filter and process ESIC numbers
    df = df[df[esic_column].notna() & (df[esic_column] != "EXEMPTED")]
    df[esic_column] = df[esic_column].astype(float).astype(int).astype(str).str.strip()
    esic_numbers = df[esic_column].tolist()
    st.write("Processed ESIC Numbers:", esic_numbers)  # Debugging line

    highlight_numbers(uan_pdf_temp_path, uan_numbers, output_uan_path, "UAN")
    highlight_numbers(esic_pdf_temp_path, esic_numbers, output_esic_path, "ESIC")

    with open(output_uan_path, "rb") as f:
        st.download_button("Download UAN Processed PDF", f, file_name=os.path.basename(output_uan_path))

    with open(output_esic_path, "rb") as f:
        st.download_button("Download ESIC Processed PDF", f, file_name=os.path.basename(output_esic_path))

    st.success(f"Processed PDFs saved as: {os.path.basename(output_uan_path)} and {os.path.basename(output_esic_path)}")
