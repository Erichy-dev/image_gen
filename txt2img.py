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
from utils.drive_utils import init_google_drive, upload_file_to_drive, get_drive_instance
from utils.excel_utils import update_product_catalog
from utils.image_processor import process_images
from config.excel import read_prompts_from_excel

console = Console()

def process_single_prompt(prompt, models, output_dir, progress):
    """Process a single prompt with the selected models"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    start_time = time.time()
    
    raw_output_dir = os.path.join(output_dir, "Digital Paper Store - Raw Folders", timestamp)
    unprocessed_output_dir = os.path.join(output_dir, "Digital Paper Store - Digital Paper", timestamp)
    processed_output_dir = os.path.join(output_dir, "Digital Paper Store - Seamless Paper", timestamp)
    
    # Create all necessary directories
    os.makedirs(raw_output_dir, exist_ok=True)
    os.makedirs(unprocessed_output_dir, exist_ok=True)
    os.makedirs(processed_output_dir, exist_ok=True)
    
    generated_paths = []
    
    # Generate images using selected models
    with ThreadPoolExecutor(max_workers=len(models)) as executor:
        futures = []
        for key, (name, client) in models:
            future = executor.submit(
                generate_single_image,
                name,
                client,
                prompt,
                raw_output_dir,
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
        # Process the generated images
        process_images(raw_output_dir, processed_output_dir)
        
        # Upload to Drive and update Excel - Simplified error handling
        drive = get_drive_instance()
        if not drive:
            console.print("[red]Error: Google Drive not initialized[/red]")
            return generated_paths

        for image_path in generated_paths:
            try:
                # Upload both raw and processed images
                raw_drive_link = upload_file_to_drive(image_path)
                processed_path = os.path.join(processed_output_dir, os.path.basename(image_path))
                processed_drive_link = upload_file_to_drive(processed_path)
                
                if raw_drive_link and processed_drive_link:
                    product_name = os.path.splitext(os.path.basename(image_path))[0]
                    excel_path = update_product_catalog(
                        product_name=product_name,
                        prompt=prompt,
                        folder_path=processed_output_dir,
                        raw_path=raw_output_dir,
                        drive_link=processed_drive_link,
                        raw_drive_link=raw_drive_link  # Add raw image link
                    )
                    console.print(f"[green]✓ Uploaded and updated catalog for: {product_name}[/green]")
                else:
                    console.print(f"[yellow]⚠ Failed to upload some files for prompt: {prompt}[/yellow]")
            
            except Exception as e:
                console.print(f"[red]Error uploading {os.path.basename(image_path)}: {str(e)}[/red]")
                continue
    
    return generated_paths

def interactive_loop(models, output_dir="Digital Paper Store"):
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

        # Read prompts from Excel
        prompts_data = read_prompts_from_excel()
        if not prompts_data:
            console.print("[red]No prompts found in Excel file[/red]")
            continue

        # Select models based on choice
        selected_models = models.items() if choice.upper() == "A" else [(choice, models[choice])]
        console.print("[yellow]Using models:[/yellow]")
        for key, (name, _) in selected_models:
            console.print(f"[yellow]- {name}[/yellow]")

        # Collect all prompts
        all_prompts = []
        for data in prompts_data:
            all_prompts.extend(data["Prompts"])

        # Process all prompts in parallel
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            with ThreadPoolExecutor(max_workers=len(all_prompts)) as executor:
                futures = []
                for prompt in all_prompts:
                    future = executor.submit(
                        process_single_prompt,
                        prompt,
                        list(selected_models),
                        output_dir,
                        progress
                    )
                    futures.append((future, prompt))
                
                for future, prompt in futures:
                    try:
                        generated_paths = future.result()
                        if not generated_paths:
                            console.print(f"[red]No images generated for prompt: {prompt}[/red]")
                    except Exception as e:
                        console.print(f"[red]Error processing prompt '{prompt}': {str(e)}[/red]")

def main():
    parser = argparse.ArgumentParser(description='Generate images from text prompt')
    parser.add_argument('--output', type=str, default='Digital Paper Store', help='Output directory for generated images')
    parser.add_argument('--upload', action='store_true', default=True, help='Upload generated images to Google Drive')
    args = parser.parse_args()
    
    try:
        console.print(Panel.fit("🚀 Starting Image Generation System", style="bold green"))
        
        # Move Google Drive initialization to the top and make it required
        try:
            init_google_drive(os.path.dirname(__file__))
            console.print("[green]✓ Google Drive initialized successfully[/green]")
        except Exception as e:
            console.print(Panel.fit(
                f"❌ Google Drive initialization failed: {e}\nPlease ensure Google Drive credentials are properly set up.",
                title="Critical Error",
                style="bold red"
            ))
            return  # Exit if Google Drive setup fails
        
        token = load_environment()
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