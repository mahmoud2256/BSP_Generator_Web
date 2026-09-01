import pandas as pd
import re
from datetime import datetime
from logger_engine import log_info, log_error
from mapping_engine import load_vendor_map
from excel_engine import build_final_excel
from pdf_engine import extract_pdf_data
from pdf2image import convert_from_path
import pytesseract
from pdf_engine import _POPPLER_PATH


# ✅ استخراج تاريخ الـ BSP من الصفحة الأولى
def extract_bsp_date(pdf_path):
    try:
        pages = convert_from_path(pdf_path, dpi=200, poppler_path=_POPPLER_PATH)
        first_page_text = pytesseract.image_to_string(pages[0], lang="eng").upper()

        match = re.search(
            r"(\d{2})-(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)-(\d{4})",
            first_page_text
        )

        if match:
            day = match.group(1)
            month = match.group(2)
            year = match.group(3)

            month_map = {
                "JAN": "1", "FEB": "2", "MAR": "3",
                "APR": "4", "MAY": "5", "JUN": "6",
                "JUL": "7", "AUG": "8", "SEP": "9",
                "OCT": "10", "NOV": "11", "DEC": "12"
            }

            mm = month_map[month]
            formatted = f"{mm}/{day}/{year}"
            return formatted, month, year

        return "2/28/2026", "FEB", "2026"

    except Exception as e:
        log_error(f"extract_bsp_date failed (falling back to default date): {e}")
        return "2/28/2026", "FEB", "2026"



def process_pdf(pdf_path, output_folder):

    try:
        log_info("=== MAIN V7 FIX HEADER ===")

        # ✅ التاريخ من PDF
        bsp_date, bsp_month, bsp_year = extract_bsp_date(pdf_path)

        # ✅ قراءة البيانات من محرك الاستخراج
        df = extract_pdf_data(pdf_path)
        if df is None or df.empty:
            log_error("No rows extracted from PDF")
            return None

        df["Amount"] = df["Amount"].astype(float)

        # ✅ تحميل vendor
        vendor_map = load_vendor_map()
        df["AL_Code"] = df["AL_Code"].astype(str).str.zfill(3)
        vendor_map["AL_Code"] = vendor_map["AL_Code"].astype(str).str.zfill(3)

        df = df.merge(vendor_map, on="AL_Code", how="left")

        df["AL_Name"] = df["AL_Name_map"].fillna("Unknown Airline")

        n = len(df)
        final = pd.DataFrame()

        # ✅ ✅ الأعمدة المطلوبة في البداية بدون أي صفوف فاضية
        final["JOURNALNAME"] = ["BSP"] * n
        final["DESCRIPTION"] = [f"BSP Payment {bsp_month}{bsp_year}-2"] * n
        final["JOURNALBATCHNUMBER"] = ["Kano-013440"] * n
        final["TRANSDATE"] = [bsp_date] * n

        # ✅ VOUCHER + LINENUMBER
        final["VOUCHER"] = ["BSP-" + str(i+1).zfill(12) for i in range(n)]
        final["LINENUMBER"] = range(1, n+1)

        # ✅ Vendor / Document / TRNC / FOP
        final["ACCOUNTTYPE"] = "Vendor"
        final["ACCOUNTDISPLAYVALUE"] = df["VENDOR"]

        final["DOCUMENT"] = "BSP/" + df["Number"].astype(str)
        final["TRNC"] = df["TRNC"]
        final["FOP"] = df["FOP"]

        # ✅ FINTAG
        final["FINTAGDISPLAYVALUE"] = df.apply(
            lambda row:
            f"bsp second payment {bsp_month.lower()} {bsp_year} | "
            f"{row['Number']} | 9020124 | Airline {row['AL_Code']} - {row['AL_Name']} "
            f"| | | | | | | | "
            f"{'Refund' if row['TRNC'] in ['RFND', '+RTDN'] else 'Sales'} | |",
            axis=1
        )

        # ✅ TEXT
        final["TEXT"] = df.apply(
            lambda r: f"bsp second payment {bsp_month} {bsp_year}",
            axis=1
        )

        # ✅ مالي
        final["CURRENCYCODE"] = "EGP"
        final["EXCHANGERATE"] = 100
        final["INVOICEDATE"] = bsp_date
        final["SALESTAXCODE"] = ""
        final["DUEDATE"] = bsp_date
        final["ITEMSALESTAXGROUP"] = ""
        final["SALESTAXGROUP"] = ""
        final["OFFSETACCOUNTDISPLAYVALUE"] = "46058"
        final["OFFSETACCOUNTTYPE"] = "Ledger"

        # ✅ Balance
        final["Balance Payable"] = df["Amount"]

        return build_final_excel(final, output_folder)

    except Exception as e:
        log_error(f"MAIN V7 FINAL ERROR: {e}")
        return None
