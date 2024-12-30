import click
import asyncio
from pathlib import Path
from .report import Report

@click.command()
@click.argument('config', type=click.Path(exists=True))
@click.argument('data', type=click.Path(exists=True), required=False)
@click.option('-o', '--output', type=click.Path(), required=True, help='Output PDF file path')
def main(config: str, data: str, output: str):
    """Generate a PDF report from configuration and data files."""
    async def generate_report():
        report = Report(config)
        await report.generate(data if data else None, output)
        click.echo(f"Report generated: {output}")

    asyncio.run(generate_report())

if __name__ == '__main__':
    main()
