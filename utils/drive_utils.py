from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import logging
from rich.console import Console

console = Console()

# Global drive instance
_drive_instance = None

def init_google_drive(project_root):
    """Initialize Google Drive connection"""
    try:
        gauth = GoogleAuth()
        # Set path to client_secrets.json
        gauth.settings['client_config_file'] = os.path.join(project_root, 'client_secrets.json')
        gauth.LocalWebserverAuth()
        drive = GoogleDrive(gauth)
        set_google_drive_instance(drive)
        console.print("[green]✓ Google Drive initialized successfully[/green]")
        return drive
    except Exception as e:
        console.print(f"[red]Error initializing Google Drive: {e}[/red]")
        raise

def set_google_drive_instance(drive):
    """Set the global drive instance"""
    global _drive_instance
    _drive_instance = drive

def get_drive_instance():
    """Get the global drive instance"""
    return _drive_instance

def upload_generated_images(output_dir, timestamp):
    """Upload the generated images to Google Drive"""
    try:
        console.print("\n[yellow]Uploading to Google Drive...[/yellow]")
        drive = get_drive_instance()
        if not drive:
            raise Exception("Google Drive not initialized")

        # Create a folder with timestamp
        folder_name = f"generated_images_{timestamp}"
        gdrive_folder = drive.CreateFile({
            'title': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        })
        gdrive_folder.Upload()
        folder_id = gdrive_folder['id']

        # Upload all files in the output directory from this generation
        uploaded_files = []
        for filename in os.listdir(output_dir):
            if timestamp in filename:  # Only upload files from this generation
                filepath = os.path.join(output_dir, filename)
                if os.path.isfile(filepath):
                    file_drive = drive.CreateFile({
                        'title': filename,
                        'parents': [{'id': folder_id}]
                    })
                    file_drive.SetContentFile(filepath)
                    file_drive.Upload()
                    uploaded_files.append(filename)
                    console.print(f"[blue]Uploaded: {filename}[/blue]")

        # Generate shareable link
        share_link = f"https://drive.google.com/drive/folders/{folder_id}?usp=sharing"
        
        if uploaded_files:
            console.print(f"[green]✓ Successfully uploaded {len(uploaded_files)} files to Google Drive[/green]")
            console.print(f"[green]📁 Drive link: {share_link}[/green]")
        return share_link
    except Exception as e:
        console.print(f"[red]Error uploading to Google Drive: {e}[/red]")
        return None 