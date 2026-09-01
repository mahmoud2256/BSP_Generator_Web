import pandas as pd
import os
from logger_engine import log_info, log_error

def build_final_excel(df, output_folder):
    try:
        output_path = os.path.join(output_folder, "BSP_OUTPUT.xlsx")

        with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Sheet1")

            workbook = writer.book
            worksheet = writer.sheets["Sheet1"]

            wrap = workbook.add_format({"text_wrap": True})
            worksheet.set_column("K:K", 50, wrap)

        log_info(f"Excel saved: {output_path}")
        return output_path

    except PermissionError as e:
        log_error(
            f"Excel writing failed (file likely open in Excel already): {e}"
        )
        return None
    except Exception as e:
        log_error(f"Excel writing failed: {e}")
        return None
