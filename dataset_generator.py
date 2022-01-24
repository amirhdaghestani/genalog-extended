from genalog.generation.document import DocumentGenerator
from genalog.generation.content import CompositeContent, ContentType
from get_bounding_boxes import get_bounding_boxes as GetBoundingBoxes
# from get_bounding_boxes_b import get_bounding_boxes as GetBoundingBoxes_b
# from get_bounding_boxes import get_bounding_boxes as GetBoundingBoxes_c
import fitz
import os

root_path = "./"
text_path = os.path.join(root_path, "texts/example.txt")
pdf_output_path = os.path.join(root_path, "output") 
with open(text_path, 'r') as f:
    text = f.read()

paragraphs = text.split('\n\n')
content_types = [ContentType.PARAGRAPH] * len(paragraphs)
content = CompositeContent(paragraphs, content_types)

default_generator = DocumentGenerator()
doc_gen = default_generator.create_generator(content, ['text_block.html.jinja'])
for doc in doc_gen:
    pdf_name_ = pdf_output_path + "/" + doc.styles["font_family"] + "_" + doc.styles["font_size"]
    pdf_name = pdf_name_ + ".pdf"
    doc.render_pdf(target=pdf_name, zoom=2)
    words, positions = GetBoundingBoxes(pdf_name, True)

# Open the pdf
doc = fitz.open(pdf_name)
for index, page in enumerate(doc):
    for position in positions[index]:
        # For every page, draw a rectangle on coordinates (1,1)(100,100)
        page.draw_rect([min(position[0], position[2]), min(position[1], position[3]), max(position[0], position[2]), max(position[1], position[3])],  color = (0, 1, 0), width = 2)
# Save pdf
doc.save(pdf_name_ + "_bbox" + ".pdf")