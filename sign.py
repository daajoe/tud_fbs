#!/usr/bin/env python3
# *-* coding: utf-8 *-*
import datetime

from OpenSSL.crypto import load_pkcs12
from PIL import Image
from endesive import pdf

now = datetime.datetime.now()
formatted = now.strftime("%d.%m.%Y %H:%M:%S %z")
signature= f'Johannes Fichte (TU Dresden)\n Digitally signed Date: {formatted}'
img = Image.open('docs/logo.png')

dct = {
    b'sigflags': 4,
    b'sigbutton': True,
    # b'signature_img': img,
    b'contact': b'johannes.fichte@tu-dresden.de',
    b'location': b'Dresden',
    #TODO: get date from DFN
    b'signingdate': now.strftime('%Y%m%d%H%M%S+02\'00\'').encode(),
    b'reason': b'Some descriptive message',
    b'signature': signature.encode(),
    #1. Gutachter
    b'signaturebox': (270, 300, 570, 370),
    b'fontsize': 10,
}

from getpass import getpass
password = getpass()

p12=load_pkcs12(open('mycertificate.p12', 'rb').read(), password)

datau = open('output/destination.pdf', 'rb').read()
# Note it does not work with the DFN timeserver (timestampurl='http://zeitstempel.dfn.de') for some reason
# was not too eager to debug; if interested consider site-packages/endesive/signer.py:175
datas = pdf.cms.sign(datau, dct, p12.get_privatekey().to_cryptography_key(), p12.get_certificate().to_cryptography(), [], 'sha256',timestampurl='http://public-qlts.certum.pl/qts-17')
with open('output/destination_signed.pdf', 'wb') as fp:
    fp.write(datau)
    fp.write(datas)

