# general libraries.
import cv2, fitz, enum
import os
# genalog libraries.
from genalog.generation.document import DocumentGenerator
from genalog.generation.content import CompositeContent, ContentType
from genalog.degradation.degrader import Degrader, ImageState
# pdf2img library.
from pdf2image import convert_from_path
# custom made library to extract bounding boxes from PDF.
from get_bounding_boxes import get_bounding_boxes as GetBoundingBoxes

# Enum class for page sizes.
class PageSize(enum.Enum):
    A3 = 0
    A4 = 1
    A5 = 2
    LETTER = 3


# define paths.
text_path = "texts/example.txt"
pdf_output_path = "output"
absolute_path = "file://" + os.path.abspath(".") + "/"

# define genalog generator.
with open(text_path, 'r') as f:
    text = f.read()
paragraphs = text.split('\n\n')
content_types = [ContentType.PARAGRAPH] * len(paragraphs)
content = CompositeContent(paragraphs, content_types)
default_generator = DocumentGenerator(template_path="./templates")
doc_gen = default_generator.create_generator(content, ['letter.html.jinja'])

# define style parameters.
font_file = "BNazanin.ttf"
font_family = font_file.split('.')[0]
img_logo = "4.png"
img_signature = "full_emza11.jpg"
page_size = PageSize.A5
letter_addressee_name = "جناب آقای مهندس [نام شخص]"
letter_addressee_title = "رئیس محترم شرکت [نام شرکت]"
new_style_combinations = {
    "hyphenate": [False],
    "font_size": ["11px"],
    "font_family": [font_family],
    "text_align": ["right"],
    "language": ["fa"],

    "absolute_path": [absolute_path],
    "font_path" : [absolute_path + "fonts/" + font_file],
    "img_logo" : [absolute_path + "images/" + img_logo],
    "img_signature" : [absolute_path + "images/" + img_signature],
    "page_size" : [page_size.value],

    "letter_addressee_name": [letter_addressee_name],
    "letter_addressee_title": [letter_addressee_title]
}

# define degeradation parameters.
DEGRADATIONS = [
    ("morphology", {"operation": "open", "kernel_shape":(9,9), "kernel_type":"plus"}),
    ("morphology", {"operation": "close", "kernel_shape":(9,1), "kernel_type":"ones"}),
    ("salt", {"amount": 0.7}),
    ("overlay", {
        "src": ImageState.ORIGINAL_STATE,
        "background": ImageState.CURRENT_STATE,
    }),
    ("bleed_through", {
        "src": ImageState.CURRENT_STATE,
        "background": ImageState.ORIGINAL_STATE,
        "alpha": 0.8,
        "offset_x": -6,
        "offset_y": -12,
    }),
    ("pepper", {"amount": 0.005}),
    ("blur", {"radius": 5}),
    ("salt", {"amount": 0.15}),
]

# applying styles and degradation.
default_generator.set_styles_to_generate(new_style_combinations)
degrader = Degrader(DEGRADATIONS)

for doc in doc_gen:
    file_name = pdf_output_path + "/" + doc.styles["font_family"] + "_" + doc.styles["font_size"]
    deg_file_name = pdf_output_path + "/" + "DEG_" + doc.styles["font_family"] + "_" + doc.styles["font_size"]
    pdf_name = file_name + ".pdf"
    # Store Pdf with convert_from_path function.
    doc.render_pdf(target=pdf_name, zoom=2)
    # doc.render_png(target=png_name, resolution=300)
    
    images = convert_from_path(pdf_name)
    for i in range(len(images)):
        png_name = file_name + "_" + str(i) + ".png"
        deg_png_name = deg_file_name + "_" + str(i) + ".png"

        # Save pages as images in the pdf.
        images[i].save(png_name, 'PNG')
        deg_image = degrader.apply_effects(cv2.imread(png_name, cv2.IMREAD_GRAYSCALE))
        cv2.imwrite(deg_png_name, deg_image)
    
    # getting bounding boxes.
    words, positions = GetBoundingBoxes(pdf_name, True)

# correction parameters for expand/collapse bounding boxes.
alpha = 1
beta = 1
for i in range(len(positions)):
    for j in range(len(positions[i])):
        positions[i][j][1] *= alpha
        positions[i][j][3] *= beta
    
# generating bounding boxes.
doc = fitz.open(pdf_name)
for index, page in enumerate(doc):
    for position in positions[index]:
        # For every page, draw a rectangle on coordinates
        page.draw_rect([min(position[0], position[2]),  min(position[1], position[3]), 
                        max(position[0], position[2]), max(position[1], position[3])],  
                        color = (0, 1, 0), width = 2)

# Save pdf
doc.save(file_name + "_bbox" + ".pdf")