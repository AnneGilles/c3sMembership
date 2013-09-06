# -*- coding: utf-8  -*-
import time
import tempfile
import subprocess
from fdfgen import forge_fdf
from c3smembership.gnupg_encrypt import encrypt_with_gnupg
from pyramid_mailer.message import (
    Message,
    Attachment,
)
DEBUG = False
#DEBUG = True


def generate_pdf(appstruct):
    """
    this function receives an appstruct
    (a datastructure received via formsubmission)
    and prepares and returns a PDF using pdftk
    """
    DEBUG = True

    fdf_file = tempfile.NamedTemporaryFile()
    pdf_file = tempfile.NamedTemporaryFile()

    #import logging
    #log = logging.getLogger(__name__)
    #log.info("test ...! ")

    import os
    here = os.path.dirname(__file__)
    declaration_pdf_de = os.path.join(here, "../pdftk/C3S-SCE-AFM-de-v01-20130905.pdf")
    declaration_pdf_en = os.path.join(here, "../pdftk/C3S-SCE-AFM-en-v01-20130905.pdf")

    # check for _LOCALE_, decide which language to use
    #print(appstruct['_LOCALE_'])
    if appstruct['_LOCALE_'] == "de":
        pdf_to_be_used = declaration_pdf_de
    elif appstruct['_LOCALE_'] == "en":
        pdf_to_be_used = declaration_pdf_en
    else:  # pragma: no cover
        # default fallback: english
        pdf_to_be_used = declaration_pdf_en

    # convert the date in date_of_birth
    #print(
    #    "generate_pdf: appstruct: date of birth: %s") % (
    #        appstruct['date_of_birth'])
    #print(
    #    "generate_pdf: type of appstruct: date of birth: %s") % type(
    #        appstruct['date_of_birth'])
    #print(
    #    "generate_pdf: str of appstruct: date of birth: %s") % str(
    #        appstruct['date_of_birth'])
    dob = time.strptime(str(appstruct['date_of_birth']), '%Y-%m-%d')
    #print("generate_pdf: date of birth: %s") % dob
    dob = time.strftime("%d.%m.%Y", dob)
    #print("generate_pdf: type of date of birth: %s") % type(dob)
    #print("generate_pdf: date of birth: %s") % dob

# here we gather all information from the supplied data to prepare pdf-filling

    fields = [
        ('FirstName', appstruct['firstname']),
        ('LastName', appstruct['lastname']),
        ('streetNo', appstruct['address1']),
        ('address2', appstruct['address2']),
        ('postcode', appstruct['postcode']),
        ('town', appstruct['city']),
        ('email', appstruct['email']),
        ('country', appstruct['country']),
        ('numshares', appstruct['num_shares']),
#        ('composer',
#         'Yes' if appstruct['activity'].issuperset(['composer']) else 'Off'),
#        ('lyricist',
#         'Yes' if appstruct['activity'].issuperset(['lyricist']) else 'Off'),
#        ('producer', 'Yes' if appstruct['activity'].issuperset(
#            ['music producer']) else 'Off'),
#        ('remixer',
#         'Yes' if appstruct['activity'].issuperset(['remixer']) else 'Off'),
#        ('dj',
#         'Yes' if appstruct['activity'].issuperset(['dj']) else 'Off'),
        #('YesDataProtection',
        #'Yes' if appstruct[
        #        #'noticed_dataProtection'] == u"(u'yes',)" else 'Off'),
#        ('inColSoc', '1' if appstruct['member_of_colsoc'] == u'yes' else '2'),
#        ('inColSocName',
#         appstruct['name_of_colsoc'] if appstruct['member_of_colsoc'] == u'yes' else ''),
#        ('URL', appstruct['opt_URL']),
#        ('bandPseudonym', appstruct['opt_band']),
#        ('investMmbr', '1' if appstruct['invest_member'] == u'yes' else '2'),
        ('dateOfBirth', dob),
    ]

# generate fdf string

    fdf = forge_fdf("", fields, [], [], [])

# write it to a file

    if DEBUG:  # pragma: no cover
        print("== prepare: write fdf")

    fdf_file.write(fdf)
    fdf_file.seek(0)  # rewind to beginning

# process the PDF, fill in prepared data

    if DEBUG:  # pragma: no cover
        print("== PDFTK: fill_form & flatten")

        print("running pdftk...")
    pdftk_output = subprocess.call(
        [
            'pdftk',
            pdf_to_be_used,  # input pdf with form fields
            'fill_form', fdf_file.name,  # fill in values
            'output', pdf_file.name,  # output file
            'flatten',  # make form read-only
            #'verbose'  # be verbose?
        ]
    )

    if DEBUG:  # pragma: no cover
        print(pdf_file.name)
    pdf_file.seek(0)

    if DEBUG:  # pragma: no cover
        print("===== pdftk output ======")
        print(pdftk_output)

# return a pdf file
    from pyramid.response import Response
    response = Response(content_type='application/pdf')
    pdf_file.seek(0)  # rewind to beginning
    response.app_iter = open(pdf_file.name, "r")

    return response


def generate_csv(appstruct):
    """
    returns a csv with the relevant data
    to ease import of new data sets
    """
    from datetime import date
    import unicodecsv
    # format:
    # date; signature; firstname; lastname; email;
    # city; country; invest_member; opt_URL; opt_band; date_of_birth;
    # composer; lyricist; producer; remixer; dj;
    # member_of_colsoc; name_of_colsoc; noticed_dataProtection

    csv = tempfile.TemporaryFile()
    csvw = unicodecsv.writer(csv, encoding='utf-8')
    fields = (
        date.today().strftime("%Y-%m-%d"),  # e.g. 2012-09-02
        'pending...',  # #                           # has signature
        appstruct['firstname'],  # #    # firstname
        appstruct['lastname'],  # #    # surname
        appstruct['email'],  # #   # email
        appstruct['city'],
        appstruct['country'],  # # # country
        'j' if appstruct['invest_member'] == 'yes' else 'n',
        appstruct['opt_URL'],
        appstruct['opt_band'],
        appstruct['date_of_birth'],
        'j' if 'composer' in appstruct['activity'] else 'n',
        'j' if 'lyricist' in appstruct['activity'] else 'n',
        'j' if 'producer' in appstruct['activity'] else 'n',
        'j' if 'remixer' in appstruct['activity'] else 'n',
        'j' if 'dj' in appstruct['activity'] else 'n',
        'j' if appstruct['member_of_colsoc'] == 'yes' else 'n',
        appstruct['name_of_colsoc'],
        'j' if appstruct['noticed_dataProtection'] == 'yes' else 'n',
    )

    csvw.writerow(fields)

    #DEBUG = True
    if DEBUG:  # pragma: no cover
        #csvr = unicodecsv.reader(csv, encoding='utf-8')
        # print for debugging? seek to beginning!
        csv.seek(0)
        #print("read one line from file: %s") % csv.readline()
        #row = csvr.next()
        #print("DEBUG: the row as list: %s") % row
    csv.seek(0)
    return csv.readline()


def make_mail_body(appstruct):
    """
    construct a multiline string to be used as the emails body
    """
    #the_activities = ''
    #for x in appstruct['activity']:
    #    the_activities += x + ', '
    #appstruct['noticed_dataProtection'] = "yes"
    # # test the types
    # for thing in [
    #     appstruct['firstname'],
    #     appstruct['lastname'],
    #     appstruct['date_of_birth'],  # .strftime("%d.%m.%Y")),  # XXX
    #     appstruct['email'],
    #     appstruct['city'],
    #     appstruct['country'],
    #     appstruct['invest_member'],
    #     appstruct['opt_URL'],
    #     appstruct['opt_band'],
    #     the_activities,
    #     appstruct['member_of_colsoc'],
    #     appstruct['name_of_colsoc'],
    #     appstruct['noticed_dataProtection'],
    # ]:
    #     print("thing: %s, type: %s") % (thing, type(thing))

    unencrypted = u"""
Yay!
we got a membership application through the form: \n
first name:                     %s
last name:                      %s
date of birth:                  %s
email:                          %s
street/no                       %s
address cont'd                  %s
city:                           %s
country:                        %s
investing member:               %s

member of coll. soc.:           %s
  name of coll. soc.:           %s

that's it.. bye!""" % (
        appstruct['firstname'],
        appstruct['lastname'],
        appstruct['date_of_birth'],  # .strftime("%d.%m.%Y")),  # XXX
        appstruct['email'],
        appstruct['address1'],
        appstruct['address2'],
        appstruct['city'],
        appstruct['country'],
        appstruct['invest_member'],
        appstruct['member_of_colsoc'],
        appstruct['name_of_colsoc'],
    )
    #if DEBUG:  # pragma: no cover
    print("the mail body: %s") % unencrypted
    return unencrypted


def accountant_mail(appstruct):
    """
    this function returns a message object for the mailer

    it consists of a mail body and an attachment attached to it
    """
    unencrypted = make_mail_body(appstruct)
    #print("accountant_mail: mail body: \n%s") % unencrypted
    #print("accountant_mail: type of mail body: %s") % type(unencrypted)
    encrypted = encrypt_with_gnupg(unencrypted)
    #print("accountant_mail: mail body (enc'd): \n%s") % encrypted
    #print("accountant_mail: type of mail body (enc'd): %s") % type(encrypted)

    message = Message(
        subject="[C3S] Yes! a new member",
        sender="noreply@c3s.cc",
        recipients=["c@c3s.cc"],
        body=encrypted
    )
    #print("accountant_mail: csv_payload: \n%s") % generate_csv(appstruct)
    #print(
    #    "accountant_mail: type of csv_payload: \n%s"
    #) % type(generate_csv(appstruct))
    csv_payload_encd = encrypt_with_gnupg(generate_csv(appstruct))
    #print("accountant_mail: csv_payload_encd: \n%s") % csv_payload_encd
    #print(
    #    "accountant_mail: type of csv_payload_encd: \n%s"
    #) % type(csv_payload_encd)

    attachment = Attachment(
        "C3S-SCE-AFM.csv.gpg", "application/gpg-encryption",
        csv_payload_encd)
    message.attach(attachment)

    return message
