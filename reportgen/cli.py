import asyncio
import json
from typing import Optional

import click
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .report import Report

app = FastAPI()
config_path: Optional[str] = None
assets_dir = Path(__file__).parent.parent / "assets"


@app.get("/", response_class=HTMLResponse)
async def serve_report():
    if config_path is None:
        raise Exception("Config path not set")

    with open(config_path) as f:
        config = json.load(f)

    report = Report(config)
    html = await report.render_html()
    return html


def run_server(host="0.0.0.0", port=8000):
    config = uvicorn.Config(
        "reportgen.cli:app",
        host=host,
        port=port,
        reload=True,
    )
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
    server = uvicorn.Server(config)
    server.run()


@click.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), help="Output file path")
@click.option("--serve", is_flag=True, help="Start FastAPI server for debugging")
@click.option("--port", default=8000, help="Port for FastAPI server")
def main(config_file: str, output: str = None, serve: bool = False, port: int = 8000):
    """Generate a report from a config file."""
    global config_path
    config_path = config_file

    if serve:
        print(f"Starting debug server at http://localhost:{port}")
        run_server(port=port)
        return

    async def generate_report():
        with open(config_file) as f:
            config = json.load(f)

        report = Report(config)
        if output:
            await report.save_pdf(output)
        else:
            output_path = Path(config_file).with_suffix(".pdf")
            await report.save_pdf(str(output_path))

    asyncio.run(generate_report())


if __name__ == "__main__":
    main()
