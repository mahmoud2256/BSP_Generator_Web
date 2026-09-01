import os
import sys


def base_dir():
    """
    المسار الحقيقي لمجلد الـ exe نفسه (مش مجلد فك الضغط المؤقت).
    استخدم الدالة دي لأي ملف لازم يكون *جنب* الـ exe فعليًا على القرص:
    logs, vendor_map csv, مجلدات Tesseract و poppler المتضمنة.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def bundle_dir():
    """
    مجلد الملفات المضمّنة جوه الـ exe نفسه عن طريق PyInstaller (datas في
    run_app.spec، زي assets/). في onefile mode ده بيبقى sys._MEIPASS
    (مجلد مؤقت)، وفي وضع التطوير العادي بيبقى نفس مجلد الملف.
    """
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", base_dir())
    return os.path.dirname(os.path.abspath(__file__))


def resource_path(*parts):
    """مسار مطلق لملف/مجلد *جنب* الـ exe (logs, vendor map, Tesseract, poppler)."""
    return os.path.join(base_dir(), *parts)


def bundled_asset_path(*parts):
    """مسار مطلق لملف متضمّن جوه الـ exe عن طريق datas في run_app.spec (زي assets/*)."""
    return os.path.join(bundle_dir(), *parts)


def writable_dir(folder_name):
    """
    مجلد قابل للكتابة دايمًا (للّوج مثلاً). لو مجلد البرنامج نفسه (Program Files
    مثلاً) مش قابل للكتابة، بترجع مسار داخل %APPDATA% بدل ما تفشل الكتابة بصمت.
    """
    primary = resource_path(folder_name)
    try:
        os.makedirs(primary, exist_ok=True)
        test_file = os.path.join(primary, ".write_test")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        return primary
    except Exception:
        fallback = os.path.join(
            os.environ.get("APPDATA", os.path.expanduser("~")),
            "BSP_Generator_Kano",
            folder_name,
        )
        os.makedirs(fallback, exist_ok=True)
        return fallback
