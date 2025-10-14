import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Paths
BASE_DIR = "."
DATA_DIR = os.path.join(BASE_DIR, "data")
IMG_DIR = os.path.join(BASE_DIR, "images")
OUTPUT_PDF = os.path.join(BASE_DIR, "final_report.pdf")

# Create document
doc = SimpleDocTemplate(OUTPUT_PDF)
styles = getSampleStyleSheet()
story = []

# --- Title ---
story.append(Paragraph("FileSystem Analysis", styles['Title']))
story.append(Spacer(1, 20))

# --- Data Section ---
for filename in sorted(os.listdir(DATA_DIR)):
    if filename.endswith(".txt"):
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, "r") as f:
            lines = f.readlines()
        
        story.append(Paragraph(f"<b>Data from {filename}:</b>", styles['Heading2']))
        for line in lines:
            story.append(Paragraph(line.strip(), styles['Normal']))
        story.append(Spacer(1, 12))

# --- Images Section ---
for filename in sorted(os.listdir(IMG_DIR)):
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
        filepath = os.path.join(IMG_DIR, filename)
        story.append(Paragraph(f"<b>Figure: {filename}</b>", styles['Heading2']))
        story.append(Image(filepath, width=400, height=300))
        story.append(Spacer(1, 20))

# --- Optional: Add a table example ---
data_table = [
    ["Metric", "Value"],
    ["Accuracy", "92.4%"],
    ["Loss", "0.13"],
    ["Epochs", "50"],
]
table = Table(data_table)
table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
    ('GRID', (0,0), (-1,-1), 1, colors.black),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
]))
story.append(Paragraph("<b>Summary Table</b>", styles['Heading2']))
story.append(table)

# --- Build PDF ---
doc.build(story)
print(f"PDF report generated: {OUTPUT_PDF}")
