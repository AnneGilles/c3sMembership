from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from c3smembership.models import initialize_sql
from c3smembership.security.request import RequestWithUserAttribute
from c3smembership.security import (
    Root,
    groupfinder
)
from pyramid_beaker import session_factory_from_settings
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    session_factory = session_factory_from_settings(settings)

    authn_policy = AuthTktAuthenticationPolicy(
        's0secret!!',
        callback=groupfinder,)
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings,
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy,
                          session_factory=session_factory,
                          root_factory=Root)
    # using a custom request with user information
    config.set_request_factory(RequestWithUserAttribute)

    config.include('pyramid_mailer')
    config.add_translation_dirs(
        'colander:locale/',
        'deform:locale/',
        'c3smembership:locale/')
    config.add_static_view('static',
                           'c3smembership:static', cache_max_age=3600)

    config.add_subscriber('c3smembership.subscribers.add_base_template',
                          'pyramid.events.BeforeRender')
    config.add_subscriber('c3smembership.subscribers.add_locale_to_cookie',
                          'pyramid.events.NewRequest')
    # home /
    # intent form
    config.add_route('join', '/')
    config.add_route('disclaimer', '/disclaimer')
    config.add_route('faq', '/faq')
    config.add_route('statute', '/statute')
    config.add_route('manifesto', '/manifesto')
    config.add_route('success', '/success')
    config.add_route('success_check_email', '/check_email')
    config.add_route('success_verify_email', '/verify/{email}/{code}')
    config.add_route('success_pdf', '/C3S_SCE_AFM_{namepart}.pdf')
    config.add_route('dashboard', '/dashboard')
    config.add_route('detail', '/detail/{memberid}')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.scan()
    return config.make_wsgi_app()
