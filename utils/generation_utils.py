from threading import Thread
from queue import Queue
import time
import os
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def generate_with_timeout(client, prompt, timeout=60):
    """Generate image in a thread with timeout"""
    result_queue = Queue()
    thread = Thread(target=lambda: result_queue.put(client.text_to_image(prompt)))
    thread.daemon = True
    
    thread.start()
    thread.join(timeout=timeout)
    
    if thread.is_alive():
        return None
    
    try:
        return result_queue.get_nowait()
    except:
        return None

def get_model_specific_prompt(base_prompt):
    """Add model-specific modifications to the prompt"""
    timestamp_seed = int(time.time() * 1000) % 1000000
    return f"{base_prompt} --seed {timestamp_seed}"

def generate_single_image(model_name, client, prompt, output_dir, timestamp, progress=None):
    """Generate and save a single image with retry logic"""
    unique_prompt = get_model_specific_prompt(prompt)
    console.print(f"[cyan]Using model: {model_name}[/cyan]")
    console.print(f"[cyan]Modified prompt: {unique_prompt}[/cyan]")
    
    max_retries = 6
    timeout = 60
    retry_delay = 3

    for attempt in range(max_retries):
        if progress:
            if 'task_id' in locals():
                progress.remove_task(task_id)
            task_id = progress.add_task(
                f"Generating {model_name} image (attempt {attempt + 1}/{max_retries})...", 
                total=None
            )

        try:
            image = generate_with_timeout(client, unique_prompt, timeout)
            
            if image is None:
                raise TimeoutError(f"Generation timed out after {timeout} seconds")
            
            image_path = os.path.join(output_dir, f"{model_name.lower()}_{timestamp}.png")
            image.save(image_path)
            
            if progress:
                progress.remove_task(task_id)
                
            console.print(f"[green]✓ {model_name} image generated successfully![/green]")
            return image_path

        except Exception as e:
            if attempt < max_retries - 1:
                console.print(f"[yellow]{model_name}: Attempt {attempt + 1} failed: {str(e)}. Retrying...[/yellow]")
                time.sleep(retry_delay)
            else:
                if progress:
                    progress.update(task_id, description=f"✗ {model_name} failed!", completed=True)
                console.print(f"[red]Failed to generate image with {model_name} after {max_retries} attempts: {str(e)}[/red]")
                return None 