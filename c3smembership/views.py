# -*- coding: utf-8 -*-

from c3smembership.utils import (
    generate_pdf,
    accountant_mail,
)
from c3smembership.models import (
    C3sMember,
    DBSession,
)

from pkg_resources import resource_filename
import colander
import deform
from deform import ValidationFailure

from pyramid.i18n import (
    #TranslationStringFactory,
    get_localizer,
    get_locale_name,
)
from pyramid.view import view_config
from pyramid.threadlocal import get_current_request
from pyramid_mailer import get_mailer
from pyramid.httpexceptions import HTTPFound

from translationstring import TranslationStringFactory

deform_templates = resource_filename('deform', 'templates')
c3smembership_templates = resource_filename('c3smembership', 'templates')

my_search_path = (deform_templates, c3smembership_templates)

_ = TranslationStringFactory('c3smembership')


def translator(term):
    #print("=== this is def translator")
    return get_localizer(get_current_request()).translate(term)

my_template_dir = resource_filename('c3smembership', 'templates/')
deform_template_dir = resource_filename('deform', 'templates/')

zpt_renderer = deform.ZPTRendererFactory(
    [
        my_template_dir,
        deform_template_dir,
    ],
    translator=translator,
)
# the zpt_renderer above is referred to within the demo.ini file by dotted name

DEBUG = False


@view_config(renderer='templates/disclaimer.pt',
             route_name='disclaimer')
def show_disclaimer(request):

    if hasattr(request, '_REDIRECT_'):
        #from pyramid.httpdexceptions import HTTPFound
        return HTTPFound(location=request.route_url('disclaimer'),
                         headers=request.response.headers)
#    locale_name = get_locale_name(request)
    # check if user clicked on language symbol to have page translated

#    if (request.query_string == '_LOCALE_=%s' % (locale_name)) or (
#        request.query_string == 'l=%s' % (locale_name)):
        # set language cookie
#        request.response.set_cookie('_LOCALE_', locale_name)
#        return HTTPFound(location=request.route_url('disclaimer'),
#                         headers=request.response.headers)

    return {'foo': 'bar'}  # dummy values: template contains all text


@view_config(renderer='templates/faq.pt',
             route_name='faq')
def show_faq(request):
    if hasattr(request, '_REDIRECT_'):  # pragma: no cover
        return HTTPFound(location=request.route_url('faq'),
                         headers=request.response.headers)
    return {'foo': 'bar'}  # dummy values: template contains all text


@view_config(renderer='templates/success.pt',
             route_name='success')
def show_success(request):
    """
    This view shows a success page with the data gathered
    and a link back to the form in case some data is wrong/needs correction
    """
    #check if user has used form or 'guessed' this URL
    if ('appstruct' in request.session):
        # we do have valid info from the form in the session
        appstruct = request.session['appstruct']
        #print("show_success: locale: %s") % appstruct['_LOCALE_']
        # gather activities for easier display in template
        activities = ''
        #for act in appstruct['activity']:
        #    #print act
        #    activities += act + ', '
        return {
            'firstname': appstruct['firstname'],
            'lastname': appstruct['lastname'],
            'activities': activities
        }
    # 'else': send user to the form
    return HTTPFound(location=request.route_url('join'))


@view_config(route_name='success_pdf')
def show_success_pdf(request):
    """
    This view just returns a PDF, given there is valid info in session
    """
    #check if user has used form or 'guessed' this URL
    if ('appstruct' in request.session):
        # we do have valid info from the form in the session
        #print("-- valid session with data found")
        # send mail to accountants // prepare a mailer
        mailer = get_mailer(request)
        # prepare mail
        appstruct = request.session['appstruct']
        the_mail = accountant_mail(appstruct)
        mailer.send(the_mail)

        return generate_pdf(request.session['appstruct'])
    # 'else': send user to the form
    #print("-- no valid session with data found")
    return HTTPFound(location=request.route_url('join'))


@view_config(
    renderer='templates/check-mail.pt',
    route_name='success_check_email')
def success_check_email(request):
    """
    This view just returns a note to go check mail
    """
    #check if user has used form or 'guessed' this URL
    if ('appstruct' in request.session):
        # we do have valid info from the form in the session
        appstruct = request.session['appstruct']
        from pyramid_mailer.message import Message
        mailer = get_mailer(request)
        # XXX TODO: check for locale, choose language for body text
        the_mail = Message(
            subject=_("C3S: confirm your email address and load your PDF"),
            sender="noreply@c3s.cc",
            recipients=[appstruct['email']],
            body="""hello %s %s,

please use this link to verify your email address
and download your personalised PDF:

https://yes.c3s.cc/verify/%s/%s
""" % (appstruct['firstname'],
       appstruct['lastname'],
       appstruct['email'],
       appstruct['email_confirm_code'])
        )
        #mailer.send(the_mail)  # XXX TODO
        import pprint
        pprint.pprint(the_mail)
        print(appstruct['email_confirm_code'])
        print(appstruct['email'])
        # DEBUG
        strrring = "http://0.0.0.0:6543/verify/" + appstruct['email_confirm_code'] + "/" + appstruct['email']
        request.session.flash(
            strrring,
            'message_above_form',
            allow_duplicate=False)
        
        # dasowohl
        # import pdb; pdb.set_trace()
        return {
            'firstname': appstruct['firstname'],
            'lastname': appstruct['lastname'],
        }
    # 'else': send user to the form
    return HTTPFound(location=request.route_url('join'))


@view_config(
    renderer='templates/verify-mail.pt',
    route_name='success_verify_email')
def success_verify_email(request):
    """
    This view is called via links sent in mails to verify mail addresses.
    It extracts both email and verification code from the URL
    and checks if there is a match in the database.
    """
    #dbsession = DBSession()
    # collect data from the URL/matchdict
    user_email = request.matchdict['email']
    confirm_code = request.matchdict['code']

    # get matching dataset from DB
    member = C3sMember.get_by_code(confirm_code)  # returns a member or None
    # check if info from DB makes sense
    # -member
    from types import NoneType
    if isinstance(member, NoneType):
        # member not found: FAIL!
        #print("a matching entry for this code was not found.")
        return {
            #'firstname': '',
            #'lastname': '',
            'namepart': '',
            'result_msg': "Not found. check URL."
        }
    elif (member.email == user_email):
        #print("-- found signee, code matches. COOL!")
        # set the email_is_confirmed flag in the DB for this signee
        member.email_is_confirmed = True
        #dbsession.flush()
        namepart = member.firstname + member.lastname
        import re
        PdfFileNamePart = re.sub(  # replace characters
            '[^a-zA-Z0-9]',  # other than these
            '_',  # with an underscore
            namepart)

        #activities = []
        #if signee.is_composer:
        #    activities.append(u'composer')
        #if signee.is_lyricist:
        #    activities.append(u'lyricist')
        #if signee.is_producer:
        #    activities.append(u'music producer')
        #if signee.is_remixer:
        #    activities.append(u'remixer')
        #if signee.is_dj:
        #    activities.append(u'dj')

        appstruct = {
            'firstname': member.firstname,
            'lastname': member.lastname,
            'email': member.email,
            'city': member.city,
            'country': member.country,
            '_LOCALE_': member.locale,
            'date_of_birth': member.date_of_birth,
            #'activity': set(activities),
            'invest_member': u'yes' if member.invest_member else u'no',
            'member_of_colsoc': u'yes' if member.member_of_colsoc else 'no',
            'name_of_colsoc': member.name_of_colsoc,
            #'opt_band': signee.opt_band,
            #'opt_URL': signee.opt_URL,
        }
        request.session['appstruct'] = appstruct
        return {
            'firstname': member.firstname,
            'lastname': member.lastname,
            'namepart': PdfFileNamePart,
            'result_msg': _("Success. Load your PDF!")
        }
    # else: code did not match OR SOMETHING...
    return {
        'firstname': '',
        'lastname': '',
        'namepart': '',
        'result_msg': "something went wrong."
    }


@view_config(renderer='templates/join.pt',
             route_name='join')
def join_c3s(request):
    """
    This is the main form view: Join C3S as member
    """
    import datetime
    from colander import Range

    LOGGING = True

    if LOGGING:  # pragma: no cover
        import logging
        log = logging.getLogger(__name__)
        log.info("join...")

    # if another language was chosen by clicking on a flag
    # the add_locale_to_cookie subscriber has planted an attr on the request
    if hasattr(request, '_REDIRECT_'):
        #print("request._REDIRECT_: " + str(request._REDIRECT_))

        _query = request._REDIRECT_
        #print("_query: " + _query)
        # set language cookie
        request.response.set_cookie('_LOCALE_', _query)
        request._LOCALE_ = _query
        locale_name = _query
        #print("locale_name (from query_string): " + locale_name)
        #from pyramid.httpexceptions import HTTPFound
        #print("XXXXXXXXXXXXXXX ==> REDIRECTING ")
        return HTTPFound(location=request.route_url('join'),
                         headers=request.response.headers)
    # # if another language was chosen, pick it
    # if request._REDIRECT_ is not '':
    #     print("request.query_string: " + str(request.query_string))
    #     _query = request.query_string
    #     print("_query: " + _query)
    #     # set language cookie
    #     request.response.set_cookie('_LOCALE_', _query)
    #     request._LOCALE_ = _query
    #     locale_name = _query
    #     print("locale_name (from query_string): " + locale_name)
    #     from pyramid.httpexceptions import HTTPFound
    #     print("XXXXXXXXXXXXXXX ==> REDIRECTING ")
    #     return HTTPFound(location=request.route_url('intent'),
    #                      headers=request.response.headers)
    else:
        #locale_name = request._LOCALE_
        locale_name = get_locale_name(request)
        #print("locale_name (from request): " + locale_name)

    # check if user clicked on language symbol to have page translated
    # #print("request.query_string: " + str(request.query_string))
    # if 'l' in request.query_string:
    #     print("request.query_string: " + str(request.query_string))
    #     print("request.query_string[0]: " + str(request.query_string[0]))

    # from pyramid.httpexceptions import HTTPFound
    # if (request.query_string == '_LOCALE_=%s' % (locale_name)) or (
    #     request.query_string == 'l=%s' % (locale_name)):
    #     # set language cookie
    #     request.response.set_cookie('_LOCALE_', locale_name)
    #     return HTTPFound(location=request.route_url('intent'),
    #                      headers=request.response.headers)

    if DEBUG:  # pragma: no cover
        print "-- locale_name: " + str(locale_name)

    country_codes = [
        ('AT', _(u'Austria')),
        ('BE', _(u'Belgium')),
        ('BG', _(u'Bulgaria')),
        ('CH', _(u'Switzerland')),
        ('CZ', _(u'Czech Republic')),
        ('DE', _(u'Germany')),
        ('DK', _(u'Denmark')),
        ('ES', _(u'Spain')),
        ('EE', _(u'Estonia')),
        ('FI', _(u'Finland')),
        ('FR', _(u'France')),
        ('GB', _(u'United Kingdom')),
        ('GR', _(u'Greece')),
        ('HU', _(u'Hungary')),
        ('HR', _(u'Croatia')),
        ('IL', _(u'Israel')),
        ('IE', _(u'Ireland')),
        ('IT', _(u'Italy')),
        ('LT', _(u'Lithuania')),
        ('LV', _(u'Latvia')),
        ('LU', _(u'Luxembourg')),
        ('MT', _(u'Malta')),
        ('NL', _(u'Netherlands')),
        ('PL', _(u'Poland')),
        ('PT', _(u'Portugal')),
        ('SK', _(u'Slovakia')),
        ('SI', _(u'Slovenia')),
        ('SE', _(u'Sweden')),
        ('XX', _(u'other'))
        ]

   # set default of Country select widget according to locale
    LOCALE_COUNTRY_MAPPING = {
        'de': 'DE',
   #    'da': 'DK',
        'en': 'GB',
   #    'es': 'ES',
   #    'fr': 'FR',
        }
    country_default = LOCALE_COUNTRY_MAPPING.get(locale_name)
    if DEBUG:  # pragma: no cover
        print("== locale is :" + str(locale_name))
        print("== choosing :" + str(country_default))

    class MembershipForm(colander.MappingSchema):
        """
        colander schema for membership application form
        """
        firstname = colander.SchemaNode(
            colander.String(),
            title=_(u"(Real) First Name"),
            oid="firstname",
            )
        lastname = colander.SchemaNode(
            colander.String(),
            title=_(u"(Real) Last Name"),
            oid="lastname",
            )
        email = colander.SchemaNode(
            colander.String(),
            title=_(u'Email'),
            validator=colander.Email(),
            oid="email",
            )
        address1 = colander.SchemaNode(
            colander.String(),
            title=_(u'Street & No.'))
        address2 = colander.SchemaNode(
            colander.String(),
            missing=unicode(''),
            title=_(u"address cont'd"))
        postCode = colander.SchemaNode(
            colander.String(),
            title=_(u'Post Code'))
        city = colander.SchemaNode(
            colander.String(),
            title=_(u'City'),
            oid="city",
            )
      #  region = colander.SchemaNode(
      #      colander.String(),
      #      title=_(u'Federal State / Province / County'),
      #      missing=unicode(''))
        country = colander.SchemaNode(
            colander.String(),
            title=_(u'Country'),
            default=country_default,
            widget=deform.widget.SelectWidget(
                values=country_codes),
            oid="country",
            )

        # type_of_creator = (('composer', _(u'composer')),
        #                    ('lyricist', _(u'lyricist')),
        #                    ('music producer', _(u'music producer')),
        #                    ('remixer', _(u'remixer')),
        #                    ('dj', _(u'DJ')))

        # activity = colander.SchemaNode(
        #     deform.Set(allow_empty=True),
        #     title=_(
        #         u"I'm musically involved in creating at least three songs, "
        #         "and I\'m considering to ask C3S to administer the rights "
        #         " to some of my songs. I am active as a "
        #         "(multiple selection possible)"),
        #     widget=deform.widget.CheckboxChoiceWidget(values=type_of_creator),
        #     missing=unicode(''),
        #     oid="activity",)

        yes_no = ((u'yes', _(u'Yes')),
                  (u'no', _(u'No')))

     #   at_least_three_works = colander.SchemaNode(
     #       colander.String(),
     #       title=_(u'I have been the (co-)creator of at least three titles '
     #               'in one of the functions mentioned under (1)'),
     #       validator=colander.OneOf([x[0] for x in yes_no]),
     #       widget=deform.widget.RadioChoiceWidget(values=yes_no))

        ## TODO: inColSocName if member_of_colsoc = yes
        ## css/jquery: fixed; TODO: validator
        def colsoc_validator(node, form):
            log.info("validating...........................................")
            #print(value['member_of_colsoc'])
            log.info(node.get('other_colsoc'))
            log.info(node.get('other_colsoc-1'))
            log.info(node.cstruct_children('other_colsoc'))
            #log.info(node.get_value('other_colsoc-1'))
            log.info(dir(node))
            #log.info(node['member_of_colsoc'])
            #import pdb; pdb.set_trace()
            #if value['member_of_colsoc']
            #exc = colander.Invalid(
            #    form, "if colsoc, give name!")
            #exc['name_of_colsoc'] = "if colsoc, give name!"
            log.info("end----------------------------------------")


        member_of_colsoc = colander.SchemaNode(
            colander.String(),
            title=_(
                u'Currently, I am a member of another collecting society.'),
            #validator=colander.OneOf([x[0] for x in yes_no]),
            widget=deform.widget.RadioChoiceWidget(values=yes_no),
            oid="other_colsoc",
            validator=colsoc_validator
            )
        name_of_colsoc = colander.SchemaNode(
            colander.String(),
            title=_(u'If so, which one?'),
            missing=unicode(''),
            oid="colsoc_name",
            validator=colander.All(
                colsoc_validator,   
                )
            )
        invest_member = colander.SchemaNode(
            colander.String(),
            title=_(
                u'I am considering to join C3S as a supporting member only. '
                'This option is also available to members of other collecting '
                'societies without quitting those.'),
            validator=colander.OneOf([x[0] for x in yes_no]),
            widget=deform.widget.RadioChoiceWidget(values=yes_no),
            oid="investing_member",
            )
        num_shares = colander.SchemaNode(
            colander.Integer(),
            title=_(u"Number of Shares (50€ each"),
            default=1,
            validator=colander.Range(
                min=1,
                max=60,
                min_err=_(u"You need at least one share of 50 Euro."),
                max_err=_(u"You may choose 60 shares at most. (3000 Euro)"),
                ),
            oid="num_shares")
       # TODO:
       # Date of birth (dd/mm/yyyy) (three fields)
       # size doesn't have any effect?!
        date_of_birth = colander.SchemaNode(
            colander.Date(),
            title=_(u'Date of Birth'),
            css_class="hasDatePicker",
            #widget = deform.widget.DatePWidget(),
            default=datetime.date(2013, 1, 1),
            validator=Range(
                min=datetime.date(1913, 1, 1),
                max=datetime.date(2000, 1, 1),
                min_err=_(u'${val} is earlier than earliest date ${min}'),
                max_err=_(u'${val} is later than latest date ${max}')
                ),
            oid="date_of_birth",
            )

        # opt_band = colander.SchemaNode(
        #     colander.String(),
        #     title=_(u'optional: Band/Artist name'),
        #     missing=u'',
        #     oid="bandname",
        #     )

        # opt_URL = colander.SchemaNode(
        #     colander.String(),
        #     title=_(u'optional: Homepage'),
        #     missing=u'',
        #     oid="bandurl",
        #     )

        #print(country_codes())
        #understood_declaration = colander.SchemaNode(
            #colander.String(),
            #title=_(u'I have read and understood the text of the '
                    #'declaration of intent.'),
##            validator=colander.OneOf(),
            #widget=deform.widget.CheckboxChoiceWidget(
                #values=(('yes', _(u'Yes')),)),
            #)
        #consider_joining = colander.SchemaNode(
            #colander.String(),
            #title=_(u'I seriously consider to join the C3S and want to '
                    #'be notified via e-mail about its foundation.'),
##            validator=colander.OneOf([x[0] for x in yes_no]),
            #widget=deform.widget.CheckboxChoiceWidget(
                #values=(('yes', _(u'Yes')),)),
            #)
#         noticed_dataProtection = colander.SchemaNode(
#             colander.String(),
#             title=_(u'I have taken note of the Data Protection Declaration '
#                     'which is part of this text and can be read separately '
#                     'at http://www.c3s.cc/disclaimer-en.html and agree with '
#                     'it. I know that I may revoke this consent at any time.'),
# #            validator=colander.OneOf([x[0] for x in yes_no]),
#             widget=deform.widget.CheckboxChoiceWidget(
#                 values=(yes_no),
#                 #    (u'yes', _(u'Yes')),
#                 #    )
#                 ),
#        )
        _LOCALE_ = colander.SchemaNode(colander.String(),
                                       widget=deform.widget.HiddenWidget(),
                                       default=locale_name)

    schema = MembershipForm()

    form = deform.Form(
        schema,
        buttons=[
            deform.Button('submit', _(u'Submit')),
            deform.Button('reset', _(u'Reset'))
        ],
        use_ajax=True,
        renderer=zpt_renderer
    )

    # if the form has been used and SUBMITTED, check contents
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
            #if DEBUG:  # pragma: no cover
            print("the appstruct from the form: %s \n") % appstruct
            for thing in appstruct:
                print("the thing: %s") % thing
                print("type: %s") % type(thing)
        except ValidationFailure, e:
            #print("the appstruct from the form: %s \n") % appstruct
            #for thing in appstruct:
            #    print("the thing: %s") % thing
            #    print("type: %s") % type(thing)
            print(e)
            #message.append(
            request.session.flash(
                _(u"Please note: There were errors, "
                  "please check the form below."),
                'message_above_form',
                allow_duplicate=False)
            return{'form': e.render()}

        def make_random_string():
            """
            used as email confirmation code
            """
            import random
            import string
            return ''.join(
                random.choice(
                    string.ascii_uppercase + string.digits
                ) for x in range(10))

        # make confirmation code and
        randomstring = make_random_string()
        # check if confirmation code is already used
        while (C3sMember.check_for_existing_confirm_code(randomstring)):
            # create a new one, if the new one already exists in the database
            randomstring = make_random_string()  # pragma: no cover

        from datetime import datetime
        from sqlalchemy.exc import InvalidRequestError
        # to store the data in the DB, an objet is created
        member = C3sMember(
            firstname=appstruct['firstname'],
            lastname=appstruct['lastname'],
            email=appstruct['email'],
            address1=appstruct['address1'],
            address2=appstruct['address2'],
            city=appstruct['city'],
            country=appstruct['country'],
            locale=appstruct['_LOCALE_'],
            date_of_birth=appstruct['date_of_birth'],
            email_is_confirmed=False,
            email_confirm_code=randomstring,
            #is_composer=('composer' in appstruct['activity']),
            #is_lyricist=('lyricist' in appstruct['activity']),
            #is_producer=('music producer' in appstruct['activity']),
            #is_remixer=('remixer' in appstruct['activity']),
            #is_dj=('dj' in appstruct['activity']),
            date_of_submission=datetime.now(),
            invest_member=(appstruct['invest_member'] == u'yes'),
            member_of_colsoc=(appstruct['member_of_colsoc'] == u'yes'),
            name_of_colsoc=appstruct['name_of_colsoc'],
            #opt_band=appstruct['opt_band'],
            #opt_URL=appstruct['opt_URL'],
            num_shares=appstruct['num_shares'],
        )
        dbsession = DBSession()
        try:
            dbsession.add(member)
            appstruct['email_confirm_code'] = randomstring
        except InvalidRequestError, e:  # pragma: no cover
            print("InvalidRequestError! %s") % e
        # send mail to accountants // prepare a mailer
        #mailer = get_mailer(request)
        # prepare mail
        #the_mail = accountant_mail(appstruct)
        #mailer.send(the_mail)
        #log.info("NOT sending mail...")

        #return generate_pdf(appstruct)  # would just return a PDF

        # redirect to success page, then return the PDF
        # first, store appstruct in session
        request.session['appstruct'] = appstruct
        #from pyramid.httpexceptions import HTTPFound
        return HTTPFound(  # redirect to success page
            location=request.route_url('success'),
        )

    # if the form was submitted and gathered info shown on the success page,
    # BUT the user wants to correct their information:
    else:
        if ('appstruct' in request.session):
            #print("form was not submitted, but found appstruct in session.")
            appstruct = request.session['appstruct']
            #print("the appstruct: %s") % appstruct
            # pre-fill the form with the values from last time
            form.set_appstruct(appstruct)
            #import pdb
            #pdb.set_trace()
            #form = deform.Form(schema,
            #           buttons=[deform.Button('submit', _(u'Submit'))],
            #           use_ajax=True,
            #           renderer=zpt_renderer
            #           )

    html = form.render()

    return {'form': html}
