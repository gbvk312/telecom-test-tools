import os
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')

def generate_report(parsed_data: dict, output_file: str):
    """
    Generates an HTML report using Jinja2 and the parsed test data.
    """
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    try:
        template = env.get_template('report.html')
    except Exception as e:
        print(f"Error loading template: {e}")
        return

    # prepare data for template
    summary = {
        "total": parsed_data.get("total", 0),
        "passed": parsed_data.get("passed", 0),
        "failed": parsed_data.get("failed", 0),
    }
    
    details = parsed_data.get("details", [])

    html_content = template.render(summary=summary, details=details)

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Report generated successfully: {output_file}")
    except Exception as e:
        print(f"Error writing report to file: {e}")
