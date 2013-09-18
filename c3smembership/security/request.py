### Making A 'User Object' Available as a Request Attribute
# docs.pylonsproject.org/projects/pyramid_cookbook/dev/authentication.html
from pyramid.decorator import reify
from pyramid.request import Request
from pyramid.security import unauthenticated_userid
from c3smembership.models import (
    C3sStaff,
    )


class RequestWithUserAttribute(Request):
    @reify
    def user(self):
        userid = unauthenticated_userid(self)
        #print "--- in RequestWithUserAttribute: userid = " + str(userid)
        if userid is not None:
            # this should return None if the user doesn't exist
            # in the database
            #return dbsession.query('users').filter(user.user_id == userid)
            return C3sStaff.check_user_or_None(userid)
        # else: userid == None
        return userid  # pragma: no cover

# /end of ### Making A 'User Object' Available as a Request Attribute
