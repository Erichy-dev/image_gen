import openpyxl
import logging
from .settings import INPUT_EXCEL_FILE

def read_prompts_from_excel(file_path=INPUT_EXCEL_FILE):
    """
    Read prompts, Product Type, Category, and Theme from the specified Excel file.
    """
    try:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        headers = [cell.value for cell in sheet[1]]

        prompts_index = headers.index("Prompts")
        theme_index = headers.index("Theme")
        category_index = headers.index("Category")
        product_type_index = headers.index("Product Type")

        data = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[prompts_index]:
                prompts = [line.strip() for line in row[prompts_index].splitlines() if line.strip()]
                data.append({
                    "Prompts": prompts,
                    "Theme": row[theme_index],
                    "Category": row[category_index],
                    "Product Type": row[product_type_index],
                    "Row Index": row[0]
                })
        return data
    except Exception as e:
        logging.error(f"Error reading Excel file: {e}")
        return [] 