import pandas as pd
import os
from datetime import datetime
from openpyxl.styles import Alignment

def update_product_catalog(product_name, prompt, folder_path, drive_link, category="Seamless Pattern"):
    """
    Create or update an Excel file with product information.
    
    Args:
        product_name (str): Name of the product
        prompt (str): The prompt used to generate the image
        folder_path (str): Path to the generated image
        drive_link (str): Google Drive sharing link
        category (str, optional): Product category. Defaults to "Seamless Pattern"
    """
    excel_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "product_catalog.xlsx")
    
    # Create new DataFrame if file doesn't exist
    if not os.path.exists(excel_path):
        df = pd.DataFrame(columns=['Product Name', 'Category', 'Prompts', 'Folder Path', 'Google Drive Link', 'Created Date'])
    else:
        df = pd.read_excel(excel_path)
    
    # Prepare new row
    new_row = {
        'Product Name': product_name,
        'Category': category,
        'Prompts': prompt,
        'Folder Path': folder_path,
        'Google Drive Link': drive_link,
        'Created Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Append new row to DataFrame
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    # Save to Excel with custom column widths and center alignment
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        worksheet = writer.sheets['Sheet1']
        
        # Set column widths and center alignment
        column_widths = {
            'A': 50,  # Product Name
            'B': 50,  # Category
            'C': 50,  # Prompts
            'D': 50,  # Folder Path
            'E': 50,  # Google Drive Link
            'F': 50   # Created Date
        }
        
        # Center align all cells including headers
        for row in worksheet.iter_rows():
            for cell in row:
                cell.alignment = Alignment(horizontal='center', vertical='center')
                
        # Set column widths
        for column, width in column_widths.items():
            worksheet.column_dimensions[column].width = width
    
    return excel_path 