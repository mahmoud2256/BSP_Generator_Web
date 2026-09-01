import pytesseract
from pdf2image import convert_from_path
import pdfplumber
import pandas as pd
import re
import os
from logger_engine import log_info, log_error
from paths import resource_path

# ✅ استخدم Tesseract و Poppler المتضمنين جنب البرنامج أولاً (بدل الاعتماد
# على تثبيت على مستوى الجهاز، اللي ممكن يتغيّر مكانه أو يتشال).
# لو مش موجودين جنب الـ exe، يرجع تلقائيًا لتثبيت النظام (لو موجود في PATH).
_BUNDLED_TESSERACT = resource_path("Tesseract", "tesseract.exe")
_BUNDLED_POPPLER_BIN = resource_path("poppler", "Library", "bin")

if os.path.isfile(_BUNDLED_TESSERACT):
    pytesseract.pytesseract.tesseract_cmd = _BUNDLED_TESSERACT
else:
    # fallback لتثبيت عادي على الجهاز
    fallback = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    pytesseract.pytesseract.tesseract_cmd = fallback if os.path.isfile(fallback) else "tesseract"

_POPPLER_PATH = _BUNDLED_POPPLER_BIN if os.path.isdir(_BUNDLED_POPPLER_BIN) else None


# تنظيف OCR
def clean_ocr(t):
    t = t.replace("O","0").replace("o","0")
    t = t.replace("I","1").replace("l","1")
    t = re.sub(r"(\d)\.(\d{3})\.(\d{2})", r"\1,\2.\3", t)
    return t


# ✅ التقاط بيانات Billing + AIR مباشرة
def extract_billing_rows(pdf_path):
    rows = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:

                txt = page.extract_text()
                if not txt:
                    continue

                for line in txt.split("\n"):

                    parts = line.split()
                    stripped = line.strip()

                    # AIR code موجود في أول عنصر
                    AIR_code = None
                    if len(parts) > 0 and re.fullmatch(r"\d{3}", parts[0]):
                        AIR_code = parts[0]

                    # Document Number
                    doc_match = re.search(r"\b(\d{10})\b", line)
                    if not doc_match:
                        continue
                    doc_num = doc_match.group(1)

                    # Amount
                    money = re.findall(r"-?\d{1,3}(?:,\d{3})*(?:\.\d{2})", line)
                    amount = float(money[-1].replace(",", "")) if money else 0.0

                    # ✅ TRNC: العمود التاني في السطر بعد كود شركة الطيران
                    # (TKTT / RFND / ADMA / ACMA / EMDS / EMDA / CANX / CANN / DCM ...)
                    # ولو السطر ده سطر مرجع لتذكرة سابقة (+RTDN / +RFND) نتعامل معاه بشكل خاص
                    if stripped.startswith("+RTDN"):
                        trnc = "+RTDN"
                    elif stripped.startswith("+RFND"):
                        trnc = "+RFND"
                    elif AIR_code and len(parts) > 1:
                        trnc = parts[1]
                    else:
                        trnc = "UNKNOWN"

                    # ✅ FOP: التوكن اللي جنب المبلغ الأول مباشرة (2-4 حروف كابيتال)،
                    # عشان عمود الـ FOP مش دايمًا في نفس الترتيب لكل أنواع المعاملات
                    FOP_val = ""
                    amt_idx = None
                    for i, p in enumerate(parts):
                        if re.fullmatch(r"-?[\d,]+\.\d{2}", p):
                            amt_idx = i
                            break
                    if amt_idx is not None and amt_idx > 0:
                        prev = parts[amt_idx - 1]
                        if re.fullmatch(r"[A-Z]{2,4}", prev):
                            FOP_val = prev

                    rows.append((AIR_code, trnc, doc_num, amount, FOP_val))

        return rows
    except Exception as e:
        log_error(f"Billing error: {e}")
        return []


# ✅ استخراج التذاكر TKTT من صفحات Issue
def extract_tickets(pdf_path):
    tickets = []
    try:
        pages = convert_from_path(pdf_path, dpi=300, poppler_path=_POPPLER_PATH)

        for page in pages:
            raw = pytesseract.image_to_string(page, lang="eng")
            cleaned = clean_ocr(raw)

            for line in cleaned.split("\n"):
                tk = re.search(r"(\d{3})[.)]?\s+TKTT\s+(\d{10})", line)
                if tk:
                    tickets.append((tk.group(1), tk.group(2)))
    except Exception as e:
        log_error(f"extract_tickets (OCR/Poppler) failed: {e}")

    return tickets


def extract_pdf_data(pdf_path):
    try:
        log_info("V8 ENGINE: Extracting FULL BSP with AIR Repair")

        bill_rows = extract_billing_rows(pdf_path)
        df_bill = pd.DataFrame(bill_rows, columns=["AIR", "TRNC", "Doc", "Amount", "FOP"])

        tk_rows = extract_tickets(pdf_path)
        df_tk = pd.DataFrame(tk_rows, columns=["TK_AIR", "Ticket"])
        df_tk["Doc"] = df_tk["Ticket"]

        # دمج TKTT + Billing
        df = df_bill.merge(df_tk, on="Doc", how="left")

        # ✅ اختيار AIR الصحيح:
        # لو TKTT موجود → استخدم TK_AIR
        # لو TKTT غير موجود → استخدم BILLING AIR
        df["AL_Code"] = df.apply(lambda r: r["TK_AIR"] if pd.notna(r["TK_AIR"]) else r["AIR"], axis=1)

        df["AL_Code"] = df["AL_Code"].fillna("000")
        df["Amount"] = df["Amount"].fillna(0.0)
        df.rename(columns={"Doc": "Number"}, inplace=True)

        log_info(df.to_string())
        return df

    except Exception as e:
        log_error(f"V8 FAILED: {e}")
        return None
