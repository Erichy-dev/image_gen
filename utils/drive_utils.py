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

def upload_file_to_drive(file_path):
    """Upload a single file to Google Drive and return its link"""
    try:
        console.print(f"\n[yellow]Uploading {os.path.basename(file_path)} to Google Drive...[/yellow]")
        drive = get_drive_instance()
        if not drive:
            raise Exception("Google Drive not initialized")

        # Create file in Drive
        file_drive = drive.CreateFile({
            'title': os.path.basename(file_path)
        })
        file_drive.SetContentFile(file_path)
        file_drive.Upload()
        
        # Make the file publicly accessible and get the link
        file_drive.InsertPermission({
            'type': 'anyone',
            'value': 'anyone',
            'role': 'reader'
        })
        
        share_link = file_drive['alternateLink']
        console.print(f"[green]✓ Successfully uploaded: {os.path.basename(file_path)}[/green]")
        console.print(f"[green]🔗 File link: {share_link}[/green]")
        
        return share_link
    except Exception as e:
        console.print(f"[red]Error uploading file to Google Drive: {e}[/red]")
        return None