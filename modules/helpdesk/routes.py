from flask import Blueprint, render_template

helpdesk_bp = Blueprint(
    "helpdesk",
    __name__,
    url_prefix="/helpdesk"
)

@helpdesk_bp.route("/")
def helpdesk():
    return render_template("helpdesk/helpdesk.html")