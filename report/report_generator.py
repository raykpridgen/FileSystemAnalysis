import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMG_DIR = os.path.join(BASE_DIR, "images")
OUTPUT_PDF = os.path.join(BASE_DIR, "final_report.pdf")

# Create document
doc = SimpleDocTemplate(OUTPUT_PDF)
styles = getSampleStyleSheet()
styles['Title'].fontName = 'Times-Bold'
styles['Title'].fontSize = 18
styles['Title'].borderPadding = (0,0,0,0)
styles['Title'].borderColor = colors.grey
styles['Title'].borderWidth = 2
styles['Title'].borderSide = 4
styles['Title'].boxTarget = 'bottom'


styles['Heading2'].fontName = 'Times-Roman'
styles['Heading2'].fontSize = 14

styles['BodyText'].fontName = 'Times-Roman'
styles['BodyText'].fontSize = 11

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

iterationTable = [
    ["Iteration", "Tree Edit Distance", "Files Added", "Change in Depth"],
]

metricsData = lines

for i in range(len(metricsData)):
    metricsData[i] = metricsData[i].strip()
    metricsData[i] = metricsData[i].split()
# --- Images Section ---
entry = 0
for filename in sorted(os.listdir(IMG_DIR)):
    #If it's the line_graph, do not try to access metrics.txt and add a table
    #Simply add the image
    if filename.lower() == "line_graph.png":
        filepath = os.path.join(IMG_DIR, filename)
        story.append(Paragraph(f"<b>Figure: {filename}</b>", styles['Heading2']))
        story.append(Image(filepath, width=400, height=300))
        story.append(Spacer(1, 20))
    #If it is not the line_graph, it is the visualize plot
    #Add the plot and a small table for each plot showcasing the relevant data
    elif filename.lower().endswith((".png", ".jpg", ".jpeg")):
        filepath = os.path.join(IMG_DIR, filename)
        story.append(Paragraph(f"<b>Figure: {filename}</b>", styles['Heading2']))
        story.append(Image(filepath, width=400, height=300))
        iterationTable.append([(entry+1), metricsData[entry][0], metricsData[entry][1], metricsData[entry][2]])
        entryTable = Table(iterationTable)
        entryTable.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Times-Roman')
        ]))
        story.append(entryTable)
        iterationTable.pop()

        story.append(Spacer(1, 20))
        entry+=1

# --- Optional: Add a table example ---
data_table = [
    ["Iteration", "Tree Edit Distance", "Files Added", "Change in Depth"],
]

iters = 1
for filename in sorted(os.listdir(DATA_DIR)):
    if filename.endswith('metrics.txt'):
        file_path = os.path.join(DATA_DIR, filename)

        with open(file_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                
                if len(parts) >= 3:
                    distance = parts[0]
                    files_added = parts[1]
                    depth_change = parts[2]

                    data_table.append([iters, distance, files_added, depth_change])
                else:
                    print(f"Skipping file {filename}: not enough values")
                iters += 1
        


table = Table(data_table)
table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
    ('GRID', (0,0), (-1,-1), 1, colors.black),
    ('FONTNAME', (0,0), (-1,0), 'Times-Roman')
]))
story.append(Paragraph("<b>Summary Table</b>", styles['Heading2']))
story.append(table)

# --- Build PDF ---
doc.build(story)
print(f"PDF report generated: {OUTPUT_PDF}")
