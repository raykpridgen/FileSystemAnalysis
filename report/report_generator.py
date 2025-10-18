import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMG_DIR = os.path.join(BASE_DIR, "images")
OUTPUT_PDF = os.path.join(BASE_DIR, "final_report.pdf")

# Create document
doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=letter)
styles = getSampleStyleSheet()

# --- Style Definitions ---
styles['Title'].fontName = 'Times-Bold'
styles['Title'].fontSize = 18
styles['Title'].borderPadding = (0, 0, 0, 0)

styles['Heading2'].fontName = 'Times-Roman'
styles['Heading2'].fontSize = 14

styles['BodyText'].fontName = 'Times-Roman'
styles['BodyText'].fontSize = 11

story = []

# --- Pre-load and Parse Metrics Data ---
parsed_metrics = []
METRICS_FILE = os.path.join(DATA_DIR, 'metrics.txt')

if os.path.exists(METRICS_FILE):
    with open(METRICS_FILE, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 3:
                parsed_metrics.append(parts)
else:
    print(f"Metrics file not found: {METRICS_FILE}")

# --- Title Section ---
story.append(Paragraph("FileSystem Analysis", styles['Title']))
# Horizontal Line using an empty table
title_line_table = Table([['']], colWidths=[doc.width])
title_line_table.setStyle(TableStyle([
    ('LINEBELOW', (0, 0), (0, 0), 2, colors.darkblue),
    ('TOPPADDING', (0, 0), (0, 0), 0),
    ('BOTTOMPADDING', (0, 0), (0, 0), 0),
]))
story.append(title_line_table)
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

# --- Images Section (Metric Plots First, then Line Graph) ---

# Separating the line_graph file from the tree plot files
all_image_files = sorted(os.listdir(IMG_DIR))
tree_plot_files = [f for f in all_image_files if f.lower().endswith((".png", ".jpg", ".jpeg")) and f.lower() != "line_graph.png"]
line_graph_file = next((f for f in all_image_files if f.lower() == "line_graph.png"), None)

entry = 0 # This index strictly maps to the tree_plot_files list and parsed_metrics

# --- Process Metric Plots (ensures correct metric pairing) ---
for filename in tree_plot_files:
    filepath = os.path.join(IMG_DIR, filename)
    figure_block = []
    
    # Check for corresponding metric data
    if entry < len(parsed_metrics):
        
        figure_block.append(Paragraph(f"<b>Figure: {filename}</b>", styles['Heading2']))
        figure_block.append(Image(filepath, width=400, height=300))
        
        # --- Table Creation ---
        single_entry_data = [
            ["Iteration", "Tree Edit Distance", "Files Added", "Change in Depth"],
            [(entry+1), parsed_metrics[entry][0], parsed_metrics[entry][1], parsed_metrics[entry][2]]
        ]
        
        entryTable = Table(single_entry_data)
        entryTable.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Times-Bold')
        ]))

        figure_block.append(entryTable)
        # --- End Table Creation ---
        
        entry += 1 # Increment index ONLY after successfully pairing data

    else:
        # Handle case where metric data runs out
        figure_block.append(Paragraph(f"<b>Figure: {filename}</b>", styles['Heading2']))
        figure_block.append(Image(filepath, width=400, height=300))
        figure_block.append(Paragraph("<i>No metric data available for this figure.</i>", styles['Normal']))

    # Wrap and append the block for the current metric figure
    story.append(KeepTogether(figure_block))
    


# --- Process Line Graph (Must be done separately and after) ---
if line_graph_file:
    filepath = os.path.join(IMG_DIR, line_graph_file)
    figure_block = [] # New block for the line graph

    figure_block.append(Paragraph(f"<b>Figure: {line_graph_file}</b>", styles['Heading2']))
    figure_block.append(Image(filepath, width=400, height=300))
    
    # Wrap and append the block for the line graph
    story.append(KeepTogether(figure_block))
    story.append(Spacer(1, 20))


# --- Summary Table Section ---
data_table = [
    ["Iteration", "Tree Edit Distance", "Files Added", "Change in Depth"],
]

#Using the parsed metrics to generate the summary table
iters = 1
for iteration in parsed_metrics:
    if len(iteration) == 3:
        distance = iteration[0]
        files_added = iteration[1]
        depth_change = iteration[2]

        data_table.append([iters, distance, files_added, depth_change])

        iters += 1
        
        
table = Table(data_table)
table.setStyle(TableStyle([
    # Enhanced Borders to separate the summary table from the sub-tables of each iteration
    ('BOX', (0, 0), (-1, -1), 2, colors.black),      # Thicker border around the entire table
    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey), # Thin grey lines for the inner grid
    ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.black), # Thicker line directly under the header
    
    # Other Styles
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
    ('FONTNAME', (0,0), (-1,0), 'Times-Bold')
]))
story.append(Paragraph("<b>Summary Table</b>", styles['Heading2']))
story.append(table)

# --- Build PDF ---
doc.build(story)
print(f"PDF report generated: {OUTPUT_PDF}")