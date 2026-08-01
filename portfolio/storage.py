from whitenoise.storage import CompressedManifestStaticFilesStorage


class ForgivingManifestStaticFilesStorage(CompressedManifestStaticFilesStorage):
    """Hashed, compressed static files — but an unresolvable name falls back to
    the plain filename instead of raising.

    Strict manifest behaviour means that forgetting `collectstatic` on a deploy
    takes the entire site down with a 500 on every page, and that the test suite
    (which runs with DEBUG=False and never collects) cannot render a template.
    A stale-cache risk is a far better failure mode than a blank site.
    """

    manifest_strict = False

    def hashed_name(self, name, content=None, filename=None):
        try:
            return super().hashed_name(name, content, filename)
        except ValueError:
            return name

    def stored_name(self, name):
        try:
            return super().stored_name(name)
        except ValueError:
            return name
