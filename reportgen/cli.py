import argparse
from pathlib import Path
from .report import Report

def main():
    parser = argparse.ArgumentParser(description='Generate PDF reports from JSON configurations')
    parser.add_argument('config', type=str, help='Path to the report configuration JSON file')
    parser.add_argument('data', type=str, help='Path to the report data JSON file')
    parser.add_argument('-o', '--output', type=str, default='report.pdf',
                       help='Output PDF file path (default: report.pdf)')
    
    args = parser.parse_args()
    
    # Create report and generate PDF
    report = Report(args.config)
    report.generate(args.data, args.output)
    print(f"Report generated: {args.output}")

if __name__ == '__main__':
    main()
