import importlib

from flask import Flask
from flask_assets import Environment, Bundle
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from os import getenv

from .core import core_app
from .db import init_databases
from .helpers import ExtensionManager, megajson


app = Flask(__name__)
valid_extensions = [ext for ext in ExtensionManager().extensions if ext.is_valid]


# optimization & security
# -----------------------

Compress(app)
Limiter(app, key_func=get_remote_address, default_limits=["1 per second"])
Talisman(
    app,
    force_https=getenv("LNBITS_WITH_ONION", 0) == 0,
    content_security_policy={
        "default-src": [
            "'self'",
            "'unsafe-eval'",
            "'unsafe-inline'",
            "blob:",
            "cdnjs.cloudflare.com",
            "code.ionicframework.com",
            "code.jquery.com",
            "fonts.googleapis.com",
            "fonts.gstatic.com",
            "maxcdn.bootstrapcdn.com",
            "github.com",
            "avatars2.githubusercontent.com",
        ]
    },
)


# blueprints / extensions
# -----------------------

app.register_blueprint(core_app)

for ext in valid_extensions:
    try:
        ext_module = importlib.import_module(f"lnbits.extensions.{ext.code}")
        app.register_blueprint(getattr(ext_module, f"{ext.code}_ext"), url_prefix=f"/{ext.code}")
    except Exception:
        raise ImportError(f"Please make sure that the extension `{ext.code}` follows conventions.")


# filters
# -------

app.jinja_env.globals["DEBUG"] = app.config["DEBUG"]
app.jinja_env.globals["EXTENSIONS"] = valid_extensions
app.jinja_env.filters["megajson"] = megajson


# assets
# ------

assets = Environment(app)
assets.url = app.static_url_path
assets.register("base_css", Bundle("scss/base.scss", filters="pyscss", output="css/base.css"))


# init
# ----


@app.before_first_request
def init():
    init_databases()


if __name__ == "__main__":
    app.run()
