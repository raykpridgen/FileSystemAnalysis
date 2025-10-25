import os
import sys
import glob
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER

# Directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../report/data")
IMG_DIR = os.path.join(BASE_DIR, "../report/images")
OUTPUT_PDF = os.path.join(BASE_DIR, "../report/final_report.pdf")


def parse_parameters(filepath):
    """Parse parameters.txt and return structured data"""
    sections = []
    current_section = None
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a section header (contains ':' but not at start)
            if 'Distribution:' in line:
                # Save previous section if exists
                if current_section:
                    sections.append(current_section)
                
                # Start new section
                parts = line.split(':', 1)
                current_section = {
                    'title': parts[0].strip(),
                    'subtitle': parts[1].strip() if len(parts) > 1 else '',
                    'label' : [],
                    'data': []
                }
            elif current_section and ':' in line:
                # This is a key-value pair
                key, value = line.split(':', 1)
                current_section['data'].append([key.strip(), value.strip()])
            
            elif current_section and ',' in line:
                # This is a label for the table
                key, value = line.split(',', 1)
                current_section['label'].append([key.strip(), value.strip()])
        
        # Add the last section
        if current_section:
            sections.append(current_section)
    
    return sections

def parse_metrics(filepath):
    """Parse metrics.txt and return structured data"""
    metrics = []
    with open(filepath, 'r') as f:
        for i, line in enumerate(f, 1):
            values = line.strip().split()
            if len(values) >= 3:
                metrics.append([f"{i}", values[0], values[1], values[2]])
    return metrics

def parse_timing(filepath):
    """Parse timing.txt and return structured data"""
    timing = []
    with open(filepath, 'r') as f:
        for line in f:
            if ':' in line:
                desc, time = line.strip().split(':', 1)
                timeVal, timeUnit = time.strip().split(' ', 1)
                if int(timeVal) > 1000 and timeUnit == 'milliseconds':
                    timeVal = str(int(timeVal) / 1000)
                    timeUnit = 'seconds'
                time = timeVal + " " + timeUnit
                timing.append([desc.strip(), time.strip()])
    return timing

def categorize_files():
    """Iterate through directories and categorize files"""
    file_data = {
        'parameters': None,
        'metrics': None,
        'timing': None,
        'line_graph': None,
        'iteration_images': []
    }
    
    # Process data directory
    if os.path.exists(DATA_DIR):
        for filename in os.listdir(DATA_DIR):
            filepath = os.path.join(DATA_DIR, filename)
            
            if not os.path.isfile(filepath):
                continue
            
            # Categorize based on filename
            if 'parameter' in filename.lower():
                file_data['parameters'] = filepath
            elif 'metric' in filename.lower():
                file_data['metrics'] = filepath
            elif 'timing' in filename.lower() or 'time' in filename.lower():
                file_data['timing'] = filepath
    
    # Process images directory
    if os.path.exists(IMG_DIR):
        for filename in os.listdir(IMG_DIR):
            filepath = os.path.join(IMG_DIR, filename)
            
            if not os.path.isfile(filepath):
                continue
            
            # Check if it's an image file
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Check if it's the line graph
                if 'line' in filename.lower() and 'graph' in filename.lower():
                    file_data['line_graph'] = filepath
                # Check if it's an iteration image (contains ':' in filename)
                elif ':' in filename:
                    # Extract iteration number for sorting
                    try:
                        iteration_num = int(filename.split(':')[0])
                        file_data['iteration_images'].append((iteration_num, filepath))
                    except ValueError:
                        # If can't extract iteration number, still add it
                        file_data['iteration_images'].append((999, filepath))
    
    # Sort iteration images by iteration number
    file_data['iteration_images'].sort(key=lambda x: x[0])
    
    return file_data

def create_pdf_report():
    """Generate the PDF report"""
    
    # Categorize all files
    file_data = categorize_files()
    
    # Create the PDF document
    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    styles['Normal'].fontName = 'Times-Roman'
    styles['Heading1'].fontName = 'Times-Roman'
    styles['Heading2'].fontName = 'Times-Roman'
    styles['Heading3'].fontName = 'Times-Roman'
    styles['Title'].fontName = 'Times-Bold'

    title_style = styles['Heading1']
    heading_style = styles['Heading2']
    subheading_style = styles['Heading3']

    heading_style.alignment = TA_CENTER
    title_style.alignment = TA_CENTER
    
    # Add main title
    elements.append(Paragraph("Simulation Report", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # ===== PARAMETERS SECTION =====
    if file_data['parameters']:
        elements.append(Paragraph("Parameters", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        param_sections = parse_parameters(file_data['parameters'])
        
        for section in param_sections:
            # Add section title and subtitle
            title_text = section['title']
            if section['subtitle']:
                title_text += f" ({section['subtitle']})"
            elements.append(Paragraph(title_text, subheading_style))
            elements.append(Spacer(1, 0.1*inch))
            
            # Create table for this section
            if section['data']:
                if section['label']:
                    table_data = [[section['label'][0][0], section['label'][0][1]]] + section['data']
                else:
                    print('Failed to load, returning')
                    sys.exit(1)
                t = Table(table_data, colWidths=[3*inch, 3*inch])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(t)
                elements.append(Spacer(1, 0.2*inch))
    
    # ===== METRICS SECTION =====
    if file_data['metrics']:
        elements.append(Paragraph("Metrics", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        metrics = parse_metrics(file_data['metrics'])
        if metrics:
            table_data = [['Iteration', 'Tree Edit Distance', 'Tree Height', 'Leaf Nodes']] + metrics
            t = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(t)
            elements.append(Spacer(1, 0.3*inch))
    
    # ===== TIMING SECTION =====
    if file_data['timing']:
        elements.append(Paragraph("Timing", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        timing = parse_timing(file_data['timing'])
        if timing:
            table_data = [['Execution', 'Time']] + timing
            t = Table(table_data, colWidths=[4*inch, 2*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(t)
            elements.append(Spacer(1, 0.3*inch))
    
    # ===== LINE GRAPH =====
    if file_data['line_graph']:
        elements.append(PageBreak())
        elements.append(Paragraph("Overall Trend", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        img = Image(file_data['line_graph'], width=6*inch, height=4*inch)
        elements.append(img)
        elements.append(Spacer(1, 0.3*inch))
    
    # ===== ITERATION IMAGES =====
    if file_data['iteration_images']:
        elements.append(PageBreak())
        elements.append(Paragraph("Iteration Details", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        for iteration_num, img_path in file_data['iteration_images']:
            # Extract iteration info from filename
            basename = os.path.basename(img_path)
            iteration_info = basename.replace('.png', '').replace('.jpg', '').replace('.jpeg', '').replace(':', ' - ')
            
            elements.append(Paragraph(f"<b>{iteration_info}</b>", subheading_style))
            elements.append(Spacer(1, 0.1*inch))
            
            # Add image
            img = Image(img_path, width=4.5*inch, height=3*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.2*inch))
            
            # Add page break every 2 images to avoid crowding
            if file_data['iteration_images'].index((iteration_num, img_path)) % 2 == 1:
                elements.append(PageBreak())
    
    # Build PDF
    doc.build(elements)
    print(f"PDF report generated: {OUTPUT_PDF}")

if __name__ == "__main__":
    create_pdf_report()