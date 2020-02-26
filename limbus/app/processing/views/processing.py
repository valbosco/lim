from flask import redirect, abort, render_template, url_for, session, request, jsonify

from flask_login import current_user

from .. import processing

from ..forms import NewProtocolForm, FluidCheckList

from ...misc.generators import generate_random_hash


@processing.route("/protocols")
def protocol_index():
    return render_template("processing/protocols/index.html")


@processing.route("/protocols/new", methods=["GET", "POST"])
def new_protocol():
    form = NewProtocolForm()
    if form.validate_on_submit():
        protocol_hash = generate_random_hash()

        session["%s protocol_information" % (protocol_hash)] = {
            "name": form.name.data,
            "type": form.type.data
        }

        return redirect(url_for('processing.new_protocol_two', hash=protocol_hash))

    return render_template("processing/protocols/new/one.html", form=form)

@processing.route("/protocols/new/two/<hash>")
def new_protocol_two(hash):

    if session["%s protocol_information" % (hash)]["type"] == "FLU":
        form = FluidCheckList()

        if form.validate_on_submit():
            session["%s fluid_steps"] = {
                "pre-cent": form.
            }

    else:
        return abort(501)

    return render_template("processing/protocols/new/two.html", form=form)
    

    