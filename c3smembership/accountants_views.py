# -*- coding: utf-8 -*-

from c3smembership.models import (
    C3sMember,
    C3sStaff,
)

from pkg_resources import resource_filename
import colander
import deform
from deform import ValidationFailure

from pyramid.i18n import (
    get_localizer,
)
from pyramid.view import view_config
from pyramid.threadlocal import get_current_request
from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    remember,
    forget,
    authenticated_userid,
)
from pyramid.url import route_url
from translationstring import TranslationStringFactory

from datetime import datetime

deform_templates = resource_filename('deform', 'templates')
c3smembership_templates = resource_filename('c3smembership', 'templates')

my_search_path = (deform_templates, c3smembership_templates)

_ = TranslationStringFactory('c3smembership')


def translator(term):
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
LOGGING = True

if LOGGING:  # pragma: no cover
    import logging
    log = logging.getLogger(__name__)


@view_config(renderer='templates/login.pt',
             route_name='login')
def accountants_login(request):
    """
    This view lets accountants log in
    """
    logged_in = authenticated_userid(request)
    #print("authenticated_userid: " + str(logged_in))

    log.info("login by %s" % logged_in)

    if logged_in is not None:  # if user is already authenticated
        return HTTPFound(  # redirect her to the dashboard
            request.route_url('dashboard',
                              number=0,))

    class AccountantLogin(colander.MappingSchema):
        """
        colander schema for login form
        """
        login = colander.SchemaNode(
            colander.String(),
            title=_(u"login"),
            oid="login",
        )
        password = colander.SchemaNode(
            colander.String(),
            validator=colander.Length(min=5, max=100),
            widget=deform.widget.PasswordWidget(size=20),
            title=_(u"password"),
            oid="lastname",
        )

    schema = AccountantLogin()

    form = deform.Form(
        schema,
        buttons=[
            deform.Button('submit', _(u'Submit')),
            deform.Button('reset', _(u'Reset'))
        ],
        #use_ajax=True,
        #renderer=zpt_renderer
    )

    # if the form has been used and SUBMITTED, check contents
    if 'submit' in request.POST:
        #print("the form was submitted")
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure, e:
            print(e)

            request.session.flash(
                _(u"Please note: There were errors, "
                  "please check the form below."),
                'message_above_form',
                allow_duplicate=False)
            return{'form': e.render()}

        # get user and check pw...
        login = appstruct['login']
        password = appstruct['password']

        try:
            checked = C3sStaff.check_password(login, password)
        except AttributeError:  # pragma: no cover
            checked = False
        if checked:
            log.info("password check for %s: good!" % login)
            headers = remember(request, login)
            log.info("logging in %s" % login)
            return HTTPFound(  # redirect to accountants dashboard
                location=route_url(  # after successful login
                    'dashboard',
                    number=0,
                    request=request),
                headers=headers)
        else:
            log.info("password check: failed.")

    html = form.render()
    return {'form': html, }


@view_config(renderer='templates/dashboard.pt',
             permission='manage',
             route_name='dashboard')
def accountants_desk(request):
    """
    This view lets accountants view applications and set their status:
    has their signature arrived? how about the payment?
    """
    _number_of_datasets = C3sMember.get_number()

    try:  # check if
        # a number us supplied with the URL
        _page_to_show = request.matchdict['number']
        # print("page to show: %s" % _page_to_show)
    except:
        _page_to_show = 0
    # is it a number?
    if not isinstance(_page_to_show, type(1)):
        _page_to_show = 0


    # how many to display on one page
    if 'num_display' in request.session:
        num_display = request.session['num_display']
    else:
        num_display = 20

    try:
        base_offset = int(_page_to_show) * num_display
        #print("base offset: %s" % base_offset)
    except:
        #base_offset = 0
        if 'base_offset' in request.session:
            base_offset = request.session['base_offset']
        else:
            base_offset = request.registry.settings['c3smembership.offset']

    # get data sets from DB
    _members = C3sMember.member_listing(
        C3sMember.id.desc(), how_many=num_display, offset=base_offset)

    # calculate next-previous-navi
    next_page = (int(_page_to_show) + 1)
    if (int(_page_to_show) > 0):
        previous_page = int(_page_to_show) - 1
    else:
        previous_page = int(_page_to_show)

    return {'_number_of_datasets': _number_of_datasets,
            'members': _members,
            'num_display': num_display,
            'next': next_page,
            'previous': previous_page,
            }


@view_config(permission='manage',
             route_name='switch_sig')
def switch_sig(request):
    """
    This view lets accountants switch member signature info
    has their signature arrived?
    """
    memberid = request.matchdict['memberid']
    #log.info("the id: %s" % memberid)

    _member = C3sMember.get_by_id(memberid)
    if _member.signature_received is True:
        _member.signature_received = False
        _member.signature_received_date = datetime(1970, 1, 1)
    elif _member.signature_received is False:
        _member.signature_received = True
        _member.signature_received_date = datetime.now()

    log.info(
        "signature status of member.id %s changed by %s to %s" % (
            _member.id,
            request.user.login,
            _member.signature_received
        )
    )

    return HTTPFound(
        request.route_url('dashboard',
                          number=0,))


@view_config(permission='manage',
             route_name='delete_entry')
def delete_entry(request):
    """
    This view lets accountants delete entries (doublettes)
    """
    memberid = request.matchdict['memberid']

    _member = C3sMember.get_by_id(memberid)

    C3sMember.delete_by_id(_member.id)
    log.info(
        "member.id %s was deleted by %s" % (
            _member.id,
            request.user.login,
        )
    )

    return HTTPFound(
        request.route_url('dashboard',
                          number=0,))


@view_config(permission='manage',
             route_name='switch_pay')
def switch_pay(request):
    """
    This view lets accountants switch member signature info
    has their signature arrived?
    """
    memberid = request.matchdict['memberid']
    _member = C3sMember.get_by_id(memberid)

    if _member.payment_received is True:  # change to NOT SET
        _member.payment_received = False
        _member_payment_received_date = datetime(1970, 1, 1)
    elif _member.payment_received is False:  # set to NOW
        _member.payment_received = True
        _member.payment_received_date = datetime.now()

    _member_payment_received_date

    log.info(
        "payment info of member.id %s changed by %s to %s" % (
            _member.id,
            request.user.login,
            _member.payment_received
        )
    )
    return HTTPFound(
        request.route_url('dashboard',
                          number=0,))


@view_config(renderer='templates/detail.pt',
             permission='manage',
             route_name='detail')
def member_detail(request):
    """
    This view lets accountants view member details
    has their signature arrived? how about the payment?
    """
    #logged_in = authenticated_userid(request)
    #log.info("detail view.................................................")
    #print("---- authenticated_userid: " + str(logged_in))

    # this following stanza is overridden by the views permission settings
    #if logged_in is None:  # not authenticated???
    #    return HTTPFound(  # go back to login!!!
    #        location=route_url(
    #            'login',
    #            request=request),
    #    )

    memberid = request.matchdict['memberid']
    #log.info("the id: %s" % memberid)

    _member = C3sMember.get_by_id(memberid)

    #print(_member)
    if _member is None:  # that memberid did not produce good results
        return HTTPFound(  # back to base
            request.route_url('dashboard',
                              number=0,))

    class ChangeDetails(colander.MappingSchema):
        """
        colander schema (form) to change details of member
        """
        signature_received = colander.SchemaNode(
            colander.Bool(),
            title=_(u"Have we received a good signature?")
        )
        payment_received = colander.SchemaNode(
            colander.Bool(),
            title=_(u"Have we received payment for the shares?")
        )

    schema = ChangeDetails()
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
        except ValidationFailure, e:  # pragma: no cover
            log.info(e)
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

        # change info about member in database

        test1 = (  # changed value through form (different from db)?
            appstruct['signature_received'] == _member.signature_received)
        if not test1:
            log.info(
                "info about signature of %s changed by %s to %s" % (
                    _member.id,
                    request.user.login,
                    appstruct['signature_received']))
            _member.signature_received = appstruct['signature_received']
        test2 = (  # changed value through form (different from db)?
            appstruct['payment_received'] == _member.payment_received)
        if not test2:
            log.info(
                "info about payment of %s changed by %s to %s" % (
                    _member.id,
                    request.user.login,
                    appstruct['payment_received']))
            _member.payment_received = appstruct['payment_received']

        # show the updated details
        HTTPFound(route_url('detail', request, memberid=memberid))

    # else: form was not submitted: just show member info and form
    html = form.render()

    return {'member': _member,
            'form': html}


@view_config(permission='view',
             route_name='logout')
def logout_view(request):
    """
    can be used to log a user/staffer off. "forget"
    """
    request.session.invalidate()
    request.session.flash(u'Logged out successfully.')
    headers = forget(request)
    return HTTPFound(location=route_url('login', request),
                     headers=headers)
