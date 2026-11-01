class SecurityHeadersMiddleware:
    """
    Pure ASGI defense-in-depth middleware that injects modern HTTP security headers
    and strips technology fingerprinting banners on all HTTP responses.
    Directly mitigates FIND-004, FIND-005, FIND-006, and FIND-007 with zero async overhead.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Extract headers
                existing_headers = list(message.get("headers", []))

                # Inject security headers
                existing_headers.append((b"x-frame-options", b"DENY"))
                existing_headers.append((b"x-content-type-options", b"nosniff"))
                existing_headers.append((
                    b"content-security-policy",
                    b"default-src 'self'; frame-ancestors 'none'; object-src 'none'; base-uri 'self';"
                ))
                existing_headers.append((b"referrer-policy", b"strict-origin-when-cross-origin"))
                existing_headers.append((b"permissions-policy", b"geolocation=(), camera=(), microphone=()"))
                existing_headers.append((
                    b"strict-transport-security",
                    b"max-age=63072000; includeSubDomains; preload"
                ))

                # Filter out fingerprinting headers
                filtered_headers = [
                    (k, v) for k, v in existing_headers
                    if k.lower() not in (b"server", b"x-powered-by")
                ]
                message["headers"] = filtered_headers

            await send(message)

        await self.app(scope, receive, send_wrapper)
