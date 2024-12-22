import pandas as pd
import os
from datetime import datetime
from openpyxl.styles import Alignment

def update_product_catalog(product_name, prompt, folder_path, raw_path, drive_link, raw_drive_link):
    """
    Create or update an Excel file with product information.
    
    Args:
        product_name (str): Name of the product
        prompt (str): The prompt used to generate the image
        folder_path (str): Path to the processed image
        raw_path (str): Path to the raw image
        drive_link (str): Google Drive sharing link
        raw_drive_link (str): Google Drive sharing link for the raw image
    """
    excel_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "product_catalog.xlsx")
    
    print(f"\n[yellow]Excel Catalog Operations:[/yellow]")
    print(f"📁 Excel file location: {excel_path}")
    print(f"📝 Updating catalog for: {product_name}")
    
    # Create new DataFrame if file doesn't exist
    if not os.path.exists(excel_path):
        print(f"[yellow]Creating new Excel catalog: {excel_path}[/yellow]")
        df = pd.DataFrame(columns=[
            'Product Name', 'Category', 'Prompts', 
            'Raw Folder Path', 'Processed Folder Path', 
            'Google Drive Link', 'Raw Google Drive Link', 'Created Date'
        ])
    else:
        print(f"[blue]Updating existing catalog: {excel_path}[/blue]")
        df = pd.read_excel(excel_path)
    
    # Prepare new row
    new_row = {
        'Product Name': product_name,
        'Category': "Seamless Pattern",
        'Prompts': prompt,
        'Raw Folder Path': raw_path,
        'Processed Folder Path': folder_path,
        'Google Drive Link': drive_link,
        'Raw Google Drive Link': raw_drive_link,
        'Created Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Print row details
    print("\n[cyan]Adding new entry:[/cyan]")
    for key, value in new_row.items():
        print(f"{key}: {value}")
    
    # Append new row to DataFrame
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    try:
        # Save to Excel with formatting
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            worksheet = writer.sheets['Sheet1']
            
            # Set column widths
            column_widths = {
                'A': 30,  # Product Name
                'B': 20,  # Category
                'C': 50,  # Prompts
                'D': 40,  # Raw Folder Path
                'E': 40,  # Processed Folder Path
                'F': 50,  # Google Drive Link
                'G': 50,  # Raw Google Drive Link
                'H': 20   # Created Date
            }
            
            # Apply formatting
            for column, width in column_widths.items():
                worksheet.column_dimensions[column].width = width
                
            # Center align all cells
            for row in worksheet.iter_rows():
                for cell in row:
                    cell.alignment = Alignment(horizontal='center', vertical='center')
            
        print(f"[green]✓ Successfully updated Excel catalog: {excel_path}[/green]")
        print(f"[green]✓ Total entries in catalog: {len(df)}[/green]")
    except Exception as e:
        print(f"[red]Error saving Excel file: {e}[/red]")
        raise
    
    return excel_path 