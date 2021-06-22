from channels.auth import AuthMiddleware
from channels.sessions import CookieMiddleware, SessionMiddleware, SessionMiddlewareStack
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from django.http import Http404
from django.contrib.sessions.models import Session
from django.utils.crypto import constant_time_compare
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import (
    get_user_model,
    HASH_SESSION_KEY,
    SESSION_KEY,
)

# custom get_user method for AuthMiddleware subclass. Mostly similar to
# https://github.com/django/channels/blob/master/channels/auth.py
@database_sync_to_async
def get_tenant_user(scope):
    """
    Return the user model instance associated with the given scope.
    If no user is retrieved, return an instance of `AnonymousUser`.
    """
    try:
        if "session" not in scope:
            raise ValueError(
                "Cannot find session in scope.\
                You should wrap your consumer in SessionMiddleware."
            )
        try:
            session_key = scope['cookies']['sessionid']
        except:
            session_key = None
        for key, value in scope.get('headers', []):
            if key == b'host':
                hostname = value.decode('ascii').split(':')[0]
        user = None
        try:
            # get session and user using django-tenants' schema_context
            #  Link: https://django-tenants.readthedocs.io/en/latest/use.html#utils
            from django_tenants.utils import get_tenant_domain_model
            domain_model = get_tenant_domain_model()
            domain = domain_model.objects.select_related('tenant').get(domain=hostname)
            try:
                tenant = domain.tenant
            except domain_model.DoesNotExist:
                raise Http404('No tenant for hostname "%s"' % hostname)
            from django.db import connection
            connection.set_tenant(tenant)

            session = Session.objects.get(session_key=session_key)
            uid = session.get_decoded().get(SESSION_KEY)
            user = get_user_model().objects.get(pk=uid)

            # Verifying the session
            # collected from:
            # https://github.com/django/channels/blob/master/channels/auth.py
            # line 44 onwards
            if hasattr(user, "get_session_auth_hash"):
                session_hash = session.get_decoded().get(HASH_SESSION_KEY)
                session_hash_verified = session_hash and constant_time_compare(
                    session_hash, user.get_session_auth_hash()
                )
                if not session_hash_verified:
                    session.flush()
                    user = None
        except:
            pass
        return user
    except:
        return AnonymousUser()


# Auth Middleware that attaches users to websocket scope on multitenant envs.
class MTAuthMiddleware(AuthMiddleware):
    async def resolve_scope(self, scope):
        scope["user"]._wrapped = await get_tenant_user(scope)


# Adds the schema name to scope and passes it down the stack of middleware ASGI apps.
# Adds a boolean as well indicating whether it's a multitenant environment or not.

@database_sync_to_async
def get_domain_model(hostname):
    from django_tenants.utils import get_tenant_domain_model
    domain_model = get_tenant_domain_model()
    domain = domain_model.objects.select_related('tenant').get(domain=hostname)
    return domain


class MTSchemaMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        if "headers" not in scope:
            raise ValueError(
                "MTSchemaMiddleware was passed a scope that did not have a headers key "
                "(make sure it is only passed HTTP or WebSocket connections)"
            )
        for key, value in scope.get('headers', []):
            if key == b'host':
                hostname = value.decode('ascii').split(':')[0]
                domain = await get_domain_model(hostname)
                try:
                    tenant = domain.tenant
                    schema_name = tenant.schema_name
                except domain.DoesNotExist:
                    raise Http404('No tenant for hostname "%s"' % hostname)
                break
        else:
            raise ValueError(
                "The headers key in the scope is invalid. "
                + "(make sure it is passed valid HTTP or WebSocket connections)"
            )
        scope["schema_name"] = schema_name
        scope["multitenant"] = True
        return await self.inner(scope, receive, send)


ChatMTMiddlewareStack = lambda inner: SessionMiddlewareStack(MTSchemaMiddleware(MTAuthMiddleware(inner)))
