import argparse
from datetime import datetime
import os
import time

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Prompt
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.model_utils import load_environment, warm_up_models
from utils.generation_utils import generate_single_image
from utils.drive_utils import init_google_drive, upload_file_to_drive
from utils.excel_utils import update_product_catalog
from utils.drive_utils import get_drive_instance

console = Console()

def interactive_loop(models, output_dir="output"):
    """Main interactive loop for generating images"""
    while True:
        console.print(Panel.fit("Available Models:", style="bold blue"))
        for key, (name, _) in models.items():
            console.print(f"{key}. {name}")
        console.print("A. All Models")
        console.print("Q. Quit")

        choice = Prompt.ask("\nSelect model(s)", choices=[*models.keys(), "A", "Q"], show_choices=False)
        
        if choice.upper() == "Q":
            break
            
        prompt = Prompt.ask("\nEnter your prompt")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        start_time = time.time()

        selected_models = models.items() if choice.upper() == "A" else [(choice, models[choice])]
        
        console.print("[yellow]Using models:[/yellow]")
        for key, (name, _) in selected_models:
            console.print(f"[yellow]- {name}[/yellow]")
        
        generated_paths = []
        with Progress(
            SpinnerColumn(), 
            TextColumn("[progress.description]{task.description}"), 
            TimeElapsedColumn(), 
            console=console
        ) as progress:
            with ThreadPoolExecutor(max_workers=len(selected_models)) as executor:
                futures = []
                for key, (name, client) in selected_models:
                    future = executor.submit(
                        generate_single_image, 
                        name, 
                        client, 
                        prompt, 
                        output_dir, 
                        timestamp,
                        progress
                    )
                    futures.append((future, name))
                
                for future, model_name in futures:
                    try:
                        image_path = future.result()
                        if image_path:
                            generated_paths.append(image_path)
                            elapsed = time.time() - start_time
                            console.print(f"[blue]{model_name} completed in {elapsed:.1f} seconds[/blue]")
                    except Exception as e:
                        console.print(f"[red]Unexpected error with {model_name}: {str(e)}[/red]")

        if generated_paths:
            elapsed_time = time.time() - start_time
            success_message = (
                f"Generation completed in {elapsed_time:.2f} seconds\n\n"
                f"📁 Generated images:\n" +
                "\n".join(f"   • [blue]{path}[/blue]" for path in generated_paths)
            )
            console.print(Panel.fit(success_message, title="Summary", style="bold green"))
            
            # Try to upload to Google Drive if initialized
            try:
                if get_drive_instance():
                    for image_path in generated_paths:
                        drive_link = upload_file_to_drive(image_path)
                        if drive_link:
                            product_name = os.path.splitext(os.path.basename(image_path))[0]
                            excel_path = update_product_catalog(
                                product_name=product_name,
                                prompt=prompt,
                                folder_path=os.path.dirname(image_path),
                                drive_link=drive_link
                            )
                    
                    console.print(f"[green]✓ Product catalog updated: {excel_path}[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠ Failed to upload to Google Drive or update catalog: {e}[/yellow]")
        else:
            console.print(Panel.fit("❌ No images were successfully generated", title="Warning", style="bold yellow"))

def main():
    parser = argparse.ArgumentParser(description='Generate images from text prompt')
    parser.add_argument('--output', type=str, default='output', help='Output directory for generated images')
    parser.add_argument('--upload', action='store_true', help='Upload generated images to Google Drive')
    args = parser.parse_args()
    
    try:
        console.print(Panel.fit("🚀 Starting Image Generation System", style="bold green"))
        token = load_environment()
        
        # Initialize Google Drive if upload flag is set
        if args.upload:
            try:
                init_google_drive(os.path.dirname(__file__))
            except Exception as e:
                console.print(f"[yellow]⚠ Google Drive initialization failed, continuing without upload capability: {e}[/yellow]")
        
        models = warm_up_models(token)
        console.print("\n[green]All models initialized and ready![/green]")
        
        interactive_loop(models, args.output)
        
    except Exception as e:
        console.print(Panel.fit(
            f"❌ {str(e)}",
            title="Error",
            style="bold red"
        ))

if __name__ == "__main__":
    main()