#!/usr/bin/env python3
from collections import OrderedDict
from io import BytesIO

from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

class PDF(object):
    def __init__(self, template):
        self.template = template
        self._existing_pdf_forms = PdfFileReader(f"{template}.pdf")
        self._existing_pdf_noforms = PdfFileReader(f"{template}_noforms.pdf")

        self.__packet = BytesIO()
        # create a new PDF with Reportlab
        self.__can = canvas.Canvas(self.__packet, pagesize=A4)

    def fill_pdf(self, content):
        self.__can.setFont("Helvetica", 12)
        positions = self._getPositions()

        x_offset, y_offset = 12, -10
        for item in content.keys():
            if item in positions:
                x_val, y_val = list(map(float, positions[item]))[:2]
                if isinstance(content[item], dict):
                    self.__can.drawString(x_val + content[item]["offset"][0], y_val + content[item]["offset"][1],
                                          content[item]["value"])
                else:
                    self.__can.drawString(x_val + x_offset, y_val + y_offset, content[item])
            else:
                self.__can.drawString(content[item]["abs"][0], content[item]["abs"][1],
                                      content[item]["value"])
        self.__can.showPage()


    @staticmethod
    def _basecase(field):
        positions = {}
        if '/Rect' in field:
            positions[field['/T']] = field['/Rect']
        else:
            positions[field['/T']] = None
        return positions

    @staticmethod
    def _traverse(tree):
        positions = {}
        if isinstance(tree, list):
            for f in tree:
                field = f.getObject()
                if '/Kids' in field:
                    for kid in field['/Kids']:
                        o = kid.getObject()
                        positions.update(PDF._traverse(o))
                else:
                    positions.update(PDF._basecase(field))
        elif isinstance(tree, dict):
            positions.update(PDF._basecase(tree))
        else:
            raise NotImplementedError("Unhandled Case. Fixme.")
        return positions

    def _getPositions(self):
        positions = {}
        catalog = self._existing_pdf_forms.trailer["/Root"]
        # get the AcroForm tree
        if "/AcroForm" in catalog:
            tree = catalog["/AcroForm"]
            if "/Fields" in tree:
                fields = tree["/Fields"]
                positions = PDF._traverse(fields)
        return positions

    def write_pdf(self, output_fh):
        self.__can.save()
        self.__packet.seek(0)

        output_pdf = PdfFileWriter()
        new_pdf = PdfFileReader(self.__packet)
        page = self._existing_pdf_noforms.getPage(0)
        output_pdf.addPage(page)

        output_pdf.getPage(0).mergePage(new_pdf.getPage(0))

        output_pdf.write(output_fh)
