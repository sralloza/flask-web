"""Base routes of the flask application."""
import logging

from flask import redirect, request, url_for
from flask.helpers import flash
from flask.templating import render_template

from app.menus.core.utils import get_last_menus_url

from . import base_blueprint

logger = logging.getLogger(__name__)


@base_blueprint.before_request
def before_request():
    """Deny access to some user agents."""
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

    return


@base_blueprint.route("/")
def index():
    """Index route."""
    return redirect(url_for("menus_blueprint.today_view"))


@base_blueprint.route("/favicon.ico")
def favicon():
    """Favicon route."""
    return redirect(url_for("static", filename="images/favicon.png"), code=301)


@base_blueprint.route("/v")
def redirect_version():
    """Route to redirect /v to /version permanently (301)."""
    return redirect(url_for("base_blueprint.version"), code=301)


@base_blueprint.route("/version")
def version():
    """Route to return the current version of the application."""
    from app import get_version

    return render_template("version.html", version=get_version())


@base_blueprint.route("/s")
def redirect_source():
    """Redirects /s to /source permanently (301)."""
    return redirect(url_for("base_blueprint.source"), code=301)


@base_blueprint.route("/source")
def source():
    """Redirects to the last menus' url."""
    return redirect(get_last_menus_url())


@base_blueprint.route("/feedback")
def feedback():
    """States the admin email to send feedback to."""
    return render_template("feedback.html")


@base_blueprint.route("/notificaciones")
@base_blueprint.route("/alertas")
@base_blueprint.route("/notifications")
@base_blueprint.route("/alerts")
def notifications():
    """Simple route to check if notifications are working."""
    flash("primary", "primary")
    flash("secondary", "secondary")
    flash("success", "success")
    flash("danger", "danger")
    flash("warning", "warning")
    flash("info", "info")
    return render_template("notifications.html")
