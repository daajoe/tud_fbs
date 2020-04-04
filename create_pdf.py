#!/usr/bin/env python3
# *-* coding: utf-8 *-*
import os

import jinja2

from tud_fbs.configuration import FbsConfig
from tud_fbs.pdf_output import PDF

config = FbsConfig(thesis_config='thesis.yml', base_config='config.yml')
fillme = config.get_filling_data()
data = config.data

o = PDF(template="docs/Anmeldung_Bachelorarbeit_neu")
o.fill_pdf(fillme)
if not os.path.exists('output'):
    os.makedirs('output')
outputname = "output/destination.pdf"
with open(outputname, "wb") as output_fh:
    o.write_pdf(output_fh)

output_email_content = "output/emailme.txt"
# Generate Template File
with open("template/email_template.txt", "r") as template_fh:
    template = jinja2.Template(template_fh.read())
    with open(output_email_content, "w") as output_email_fh:
        output_email_fh.write(template.render(data))
