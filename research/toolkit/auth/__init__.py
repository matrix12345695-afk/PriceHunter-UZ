from .tracer import AuthTracer

__all__ = [
    "AuthTracer",
]

self.summary = {
    "authorization_headers": [],
    "set_cookie": [],
    "cookies": [],
    "graphql": [],
    "x_iid": [],
}

self._seen = {
    "authorization_headers": set(),
    "set_cookie": set(),
    "cookies": set(),
    "graphql": set(),
    "x_iid": set(),
}