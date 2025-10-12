import os
import tempfile
from fpdf import FPDF
from dotenv import load_dotenv
from datetime import datetime

def load_env_variables():
    """Loads environment variables from .env file into os.environ"""
    load_dotenv()
    return os.environ

def format_datetime(dt_str, input_format="%Y-%m-%d", output_format="%d %b %Y"):
    """
    Format a datetime string from one format to another.
    Example:
        format_datetime("2025-08-09") -> "09 Aug 2025"
    """
    try:
        dt = datetime.strptime(dt_str, input_format)
        return dt.strftime(output_format)
    except Exception as e:
        raise ValueError(f"Invalid date format: {e}")

def export_to_pdf(itinerary_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    try:
        for line in itinerary_text.split("\n"):
            line = line.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 10, line)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(temp_file.name)
        return temp_file.name
    except Exception as e:
        raise Exception(f"PDF generation failed: {str(e)}")
