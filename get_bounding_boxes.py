from pdfminer.layout import LAParams, LTChar, LTTextBox, LTTextLine
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
import re

def get_bounding_boxes(path, print_output = False ):
    fp = open(path, 'rb')
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    pages = PDFPage.get_pages(fp)

    page_words = []
    page_positions = []

    for page in pages:
        if (print_output):
            print('x1\ty1\tx2\ty2\tword\n---\t---\t---\t---\t---')
        interpreter.process_page(page)
        layout = device.get_result()

        words = []
        positions = []
        word = ""
        height_low = 0
        height_high = 10000
        for lobj in layout:
            if isinstance(lobj, LTTextBox):
                for liobj in lobj:
                    if isinstance(liobj, LTTextLine):
                        for chobj in liobj:
                            if isinstance(chobj, LTChar):

                                if (word == "" and chobj.get_text() == " "):
                                    continue
                                
                                if (word != "" and word != " " and (not(isEnglish(word[-1]) and isPunctuation(chobj.get_text()))) and (isEnglish(word[-1]) != isEnglish(chobj.get_text()))):
                                    words.append(word)
                                    if (isEnglish(word)):
                                        positions.append([start[0], height_low, end[0], height_high])
                                    else:
                                        positions.append([start[0], height_low, end[0], height_high])
                                    word = ""

                                if (word != "" and min(chobj.bbox[1], chobj.bbox[3]) < height_low):
                                    words.append(word)
                                    if (isEnglish(word)):
                                        positions.append([start[0], height_low, end[0], height_high])
                                    else:
                                        positions.append([start[0], height_low, end[0], height_high])
                                    word = ""

                                if (word == "" and chobj.get_text() != " "):
                                    height_low = min(chobj.bbox[1], chobj.bbox[3])
                                    height_high = max(chobj.bbox[1], chobj.bbox[3])

                                    if (isEnglish(chobj.get_text())):
                                        start = [min(chobj.bbox[0], chobj.bbox[2]), min(chobj.bbox[1], chobj.bbox[3])]
                                        end = [max(chobj.bbox[0], chobj.bbox[2]), min(chobj.bbox[1], chobj.bbox[3])]
                                    else:
                                        start = [max(chobj.bbox[0], chobj.bbox[2]), min(chobj.bbox[1], chobj.bbox[3])]
                                        end = [min(chobj.bbox[0], chobj.bbox[2]), min(chobj.bbox[1], chobj.bbox[3])]                                
                                    word = word + chobj.get_text()
                                elif (word != "" and chobj.get_text() == " " or chobj.get_text() == "\t" or chobj.get_text() == "\n"):
                                    words.append(word)
                                    if (isEnglish(word)):
                                        positions.append([start[0], height_low, end[0], height_high])
                                    else:
                                        positions.append([start[0], height_low, end[0], height_high])
                                    word = ""
                                elif (word != ""):
                                    height_low = min(chobj.bbox[1], chobj.bbox[3]) if min(chobj.bbox[1], chobj.bbox[3]) < height_low else height_low
                                    height_high = max(chobj.bbox[1], chobj.bbox[3]) if max(chobj.bbox[1], chobj.bbox[3]) > height_high else height_high
                                    if (isEnglish(chobj.get_text()) or (isPunctuation(chobj.get_text()) and isEnglish(word[-1])) ):
                                        end = [max(chobj.bbox[0], chobj.bbox[2]), min(chobj.bbox[1], chobj.bbox[3])]
                                    else:
                                        end = [min(chobj.bbox[0], chobj.bbox[2]), min(chobj.bbox[1], chobj.bbox[3])]
                                    word = word + chobj.get_text()

                if (print_output):
                    for index, w in enumerate(words):
                        print('%d\t%d\t%d\t%d\t%s\n' % (positions[index][0], positions[index][1], positions[index][2], positions[index][3], w))

        page_words.append(words)
        page_positions.append(positions)

    return page_words, page_positions

def isEnglish(s):
  reg = re.compile(r'[a-zA-Z]')
  return bool(reg.match(s))

def isPunctuation(s):
    reg = re.compile(r'[.!?\\-]')
    return bool(reg.match(s))