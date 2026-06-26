import markdown
import pdfkit

# Read the markdown file
with open('FINAL_REPORT_DRAFT.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Convert markdown to html
html = markdown.markdown(text, extensions=['extra'])

# Add some basic styling
html_with_style = f"""
<html>
<head>
<style>
body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }}
h1, h2, h3 {{ color: #333; }}
h1 {{ border-bottom: 2px solid #333; padding-bottom: 10px; }}
code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 4px; }}
blockquote {{ border-left: 4px solid #ccc; margin-left: 0; padding-left: 16px; font-style: italic; color: #555; }}
</style>
</head>
<body>
{html}
</body>
</html>
"""

# Options for pdfkit
options = {
    'page-size': 'A4',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
    'no-outline': None
}

# Convert HTML to PDF
pdfkit.from_string(html_with_style, 'TTTC2343_Final_Report_Autonomous_Warehouse_Robot_Group_11_Compiled.pdf', options=options)
print("Successfully compiled to TTTC2343_Final_Report_Autonomous_Warehouse_Robot_Group_11_Compiled.pdf")
