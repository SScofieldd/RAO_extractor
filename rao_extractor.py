import pdfplumber
import pandas as pd

def extract_tables_from_pdf(pdf_path, page_range, output_excel, progress_data=None):
    logs = []
    if '-' in page_range:
        start, end = map(int, page_range.split('-'))
        pages_to_extract = list(range(start, end + 1))
    else:
        pages_to_extract = [int(page_range)]
    total_pages = len(pages_to_extract)
    all_tables = {}
    last_sheet = None

    def is_header_row(row):
        return row and any("Heading" in str(cell) for cell in row)

    with pdfplumber.open(pdf_path) as pdf:
        for idx, i in enumerate(pages_to_extract):
            try:
                logs.append(f"📄 Processing Page {i}...")
                page = pdf.pages[i - 1]
                tables = page.extract_tables()
                for j, table in enumerate(tables):
                    if not table or not table[0]:
                        continue
                    if is_header_row(table[0]):
                        df = pd.DataFrame(table[1:], columns=table[0])
                        sheet_name = f"Page_{i}"
                        if sheet_name in all_tables:
                            sheet_name = f"Page_{i}_Part{j+1}"
                        all_tables[sheet_name] = df
                        last_sheet = sheet_name
                        logs.append(f"✅ New Heading found → {sheet_name}")
                    else:
                        if last_sheet:
                            df = pd.DataFrame(table)
                            existing = all_tables[last_sheet]
                            if df.shape[1] == existing.shape[1]:
                                df.columns = existing.columns
                                all_tables[last_sheet] = pd.concat([existing, df], ignore_index=True)
                                logs.append(f"↪ Appended continuation rows to {last_sheet}")
                            else:
                                logs.append(f"⚠️ Skipped table on Page {i}, Table {j+1} — column mismatch")
            except IndexError:
                logs.append(f"❌ Page {i} not found.")

            if progress_data is not None:
                progress_data["progress"] = int(((idx + 1) / total_pages) * 80)

    if all_tables:
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            for sheet_name, df in all_tables.items():
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
        logs.append(f"✅ Extracted {len(all_tables)} tables to: {output_excel}")
    else:
        logs.append("⚠️ No tables found.")

    return logs, output_excel


def extract_custom_page(pdf_path, page_number, output_excel):
    logs = []
    with pdfplumber.open(pdf_path) as pdf:
        try:
            page = pdf.pages[int(page_number) - 1]
            logs.append(f"📄 Extracting from Page {page_number}...")
            tables = page.extract_tables()
            text = page.extract_text()
            with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                if tables:
                    for i, table in enumerate(tables):
                        df = pd.DataFrame(table[1:], columns=table[0])
                        df.to_excel(writer, sheet_name=f"Table_{i+1}", index=False)
                    logs.append("✅ Tables extracted successfully.")
                elif text:
                    pd.DataFrame([[text]]).to_excel(writer, sheet_name="Text", index=False, header=False)
                    logs.append("✅ Text extracted successfully.")
                else:
                    logs.append("⚠️ No content found.")
        except Exception as e:
            logs.append(f"❌ Error: {e}")
    return logs
