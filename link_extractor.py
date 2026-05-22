import sys
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

# Import Rich components for the beautiful 🥺 terminal UI
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

console = Console()

def is_valid_url(url: str) -> bool:
    """Basic validation to check if the URL has a valid scheme and network location."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def extract_links(url: str):
    """Fetches the webpage and extracts all unique anchor links."""
    # Add a header so servers don't instantly block the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # Using console.status creates an animated live spinner
    with console.status(f"[bold text.cyan]Scraping [underline]{url}[/... ", spinner="dots"):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            console.print(f"\n[bold red]Error fetching the URL:[/bold red] {e}\n")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        anchors = soup.find_all("a", href=True)

    if not anchors:
        console.print("[yellow]No links found on this page.[/yellow]\n")
        return

    # Track unique links to avoid duplicates
    unique_links = {}
    for anchor in anchors:
        href = anchor["href"].strip()
        text = anchor.get_text().strip() or "[No Text/Image Link]"
        
        # Truncate overly long link text for table neatness
        if len(text) > 40:
            text = text[:37] + "..."
            
        # Resolve relative URLs (e.g., /about -> https://example.com/about)
        absolute_url = urljoin(url, href)
        
        # Clean up fragments/anchors (e.g., #top) if you just want the base target page
        # Remove the next line if you want to keep specific page fragments distinct
        absolute_url = urlparse(absolute_url)._replace(fragment="").geturl()

        if absolute_url not in unique_links:
            unique_links[absolute_url] = text

    # Display the results in a Rich Table
    table = Table(title=f"\nFound {len(unique_links)} Unique Links", expand=True, box=None)
    table.add_column("Index", justify="right", style="cyan", no_wrap=True)
    table.add_column("Link Text/Context", style="magenta")
    table.add_column("URL", style="green")

    for idx, (link_url, link_text) in enumerate(unique_links.items(), 1):
        table.add_row(str(idx), link_text, link_url)

    console.print(table)
    console.print("-" * console.width)

def main():
    # Show a welcoming UI Panel
    console.print(
        Panel.fit(
            "[bold reversed cyan]  LINK EXTRACTOR  [/]\n\n"
            "An interactive terminal tool to extract and map out webpage links.",
            border_style="cyan",
        )
    )

    while True:
        try:
            # Prompt user for input interactively
            target_url = Prompt.ask("[bold green]Enter a website URL[/] (or type 'exit' to quit)")
            
            if target_url.lower() in ["exit", "quit", "q"]:
                console.print("[bold italic yellow]Happy browsing! Goodbye.[/]")
                sys.exit(0)

            # Automatically fix missing protocol if the user types 'google.com'
            if not target_url.startswith(("http://", "https://")):
                target_url = "https://" + target_url

            if not is_valid_url(target_url):
                console.print("[bold red]❌ Invalid URL format. Please try again.[/]\n")
                continue

            extract_links(target_url)

        except KeyboardInterrupt:
            console.print("\n[bold yellow]Process interrupted by user. Exiting...[/]")
            break

if __name__ == "__main__":
    main()