import logging

from flask import redirect, request, url_for
from flask.helpers import flash
from flask.templating import render_template

from app.menus.core.utils import get_last_menus_url

from . import base_blueprint

logger = logging.getLogger(__name__)


@base_blueprint.before_request
def before_request():
    user_agent = request.headers.get("User-Agent")

    if user_agent is None:
        return "A user agent must be provided", 401

    lowercase_user_agent = user_agent.lower()

    if "rift" in lowercase_user_agent:
        logger.debug("Detected Rift as user agent (%r)", user_agent)
        return "Rift not allowed", 401
    if "python" in lowercase_user_agent:
        logger.debug("Detected Python as user agent (%r)", user_agent)
        return "Python requests not allowed", 401
    if "yandex" in lowercase_user_agent:
        logger.debug("Detected Yandex as user agent (%r)", user_agent)
        return "Yandex bots are not allowed", 401
    if "smtbot" in lowercase_user_agent:
        logger.debug("Detected SMT as user agent (%r)", user_agent)
        return "SMT Bots are not allowed", 401
    if "nimbostratus" in lowercase_user_agent:
        logger.debug("Detected Nimbostratus as user agent (%r)", user_agent)
        return "Nimbostratus bots are not allowed", 401
    if "bot" in lowercase_user_agent:
        logger.warning("Detected unkown bot as user agent (%r)", user_agent)
        return "Bots are not allowed", 401
    if user_agent == "-":
        logger.debug("Not user agent provided (%r)", user_agent)
        return "A user agent must be provided", 401


@base_blueprint.route("/")
def index():
    return redirect(url_for("menus_blueprint.today_view"))


@base_blueprint.route("/favicon.ico")
def favicon():
    return redirect(url_for("static", filename="images/favicon.png"), code=301)


@base_blueprint.route("/v")
def redirect_version():
    return redirect(url_for("base_blueprint.version"), code=301)


@base_blueprint.route("/version")
def version():
    from app import get_version

    return "<h1>Current version=%s" % get_version() + "</h1>"


@base_blueprint.route("/s")
def redirect_source():
    return redirect(url_for("base_blueprint.source"), code=301)


@base_blueprint.route("/source")
def source():
    return redirect(get_last_menus_url())


@base_blueprint.route("/feedback")
def feedback():
    return "<h1>Send feedback to sralloza@gmail.com</h1>"


@base_blueprint.route("/a")
def redirect_aemet():
    return redirect(url_for("base_blueprint.aemet"), code=301)


@base_blueprint.route("/aemet")
def aemet():
    return redirect(
        "http://www.aemet.es/es/eltiempo/prediccion/municipios/horas/tabla/valladolid-id47186",
        code=301,
    )


@base_blueprint.route("/notificaciones")
@base_blueprint.route("/notifications")
def asdfsdaffdsfas():
    flash("primary", "primary")
    flash("secondary", "secondary")
    flash("success", "success")
    flash("danger", "danger")
    flash("warning", "warning")
    flash("info", "info")
    return render_template("base.html")
