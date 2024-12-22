from huggingface_hub import InferenceClient
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
from threading import Thread
from queue import Queue

console = Console()

def load_environment():
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    token = os.getenv("TOKEN")
    if not token:
        raise ValueError("TOKEN not found in .env file")
    return token

def warm_up_models(token, timeout=10):
    """Initialize and warm up all models with timeout"""
    console.print(Panel.fit("🎨 Initializing AI Models", style="bold magenta"))
    models = {
        "1": ("Flux", InferenceClient("strangerzonehf/Flux-Midjourney-Mix2-LoRA", token=token, timeout=30)),
        "2": ("Midjourney", InferenceClient("Jovie/Midjourney", token=token, timeout=30)),
        "3": ("Seamless", InferenceClient("prithivMLmods/Seamless-Pattern-Design-Flux-LoRA", token=token, timeout=30)),
        "4": ("Nercy", InferenceClient("Nercy/flux-dalle", token=token, timeout=30))
    }
    
    start_time = time.time()
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        for key, (name, client) in models.items():
            if time.time() - start_time > timeout:
                console.print(f"[yellow]⚠ Warm-up taking too long, skipping remaining models[/yellow]")
                break
                
            task = progress.add_task(f"Warming up {name}...", total=None)
            try:
                def warm_up():
                    return client.text_to_image("test")
                
                q = Queue()
                thread = Thread(target=lambda: q.put(warm_up()))
                thread.daemon = True
                thread.start()
                
                thread.join(timeout=2)
                
                if thread.is_alive():
                    raise TimeoutError(f"Warm-up for {name} timed out")
                    
                progress.update(task, completed=True)
                console.print(f"[green]✓ {name} ready[/green]")
                
            except Exception as e:
                progress.update(task, completed=True)
                console.print(f"[yellow]⚠ {name} warm-up skipped: {str(e)}[/yellow]")
                continue
    
    elapsed = time.time() - start_time
    console.print(f"[blue]Model initialization completed in {elapsed:.1f} seconds[/blue]")
    return models 