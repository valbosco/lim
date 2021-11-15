# Copyright (C) 2021  Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import requests
from .. import sample
from flask_login import login_required
from flask import json, render_template, url_for, redirect, flash, request, jsonify
from ...misc import get_internal_api_header
from ..forms import SampleShipmentEventForm, SampleShipmentStatusUpdateform
from datetime import datetime
from ..enums import SampleShipmentStatusStatus


@sample.route("/shipment/cart")
@login_required
def shipment_cart():
    return render_template("sample/shipment/cart.html")


@sample.route("/shipment/cart/data")
@sample.route("/shipment/new/data")
@login_required
def shipment_cart_data():
    cart_response = requests.get(
        url_for("api.get_cart", _external=True),
        headers=get_internal_api_header(),
    )

    return (
        cart_response.text,
        cart_response.status_code,
        cart_response.headers.items(),
    )


@sample.route("/shipment")
@login_required
def shipment_index():
    return render_template("sample/shipment/index.html")


@sample.route("/shipment/data")
@login_required
def shipment_index_data():
    shipment_response = requests.get(
        url_for("api.shipment_index", _external=True), headers=get_internal_api_header()
    )

    return (
        shipment_response.text,
        shipment_response.status_code,
        shipment_response.headers.items(),
    )


@sample.route("/shipment/view/<uuid>")
@login_required
def shipment_view_shipment(uuid):
    return render_template("sample/shipment/view.html", uuid=uuid)


@sample.route("/shipment/update_status/<uuid>", methods=["GET", "POST"])
@login_required
def shipment_update_status(uuid):
    shipment_response = requests.get(
        url_for("api.shipment_view_shipment", uuid=uuid, _external=True),
        headers=get_internal_api_header(),
    )

    if shipment_response.status_code == 200:
        shipment_info = {}
        status = shipment_response.json()["content"]["status"]
        if status in ["", None]:
            shipment_info["status"] = "TBC"
        else:
            shipment_info["status"] = SampleShipmentStatusStatus(status).name

        if shipment_info["status"] in ["DEL", "UND", "CAN"]:
            flash("The shipment has been closed! ")
            return redirect(url_for("sample.shipment_view_shipment", uuid=uuid))

        form = SampleShipmentStatusUpdateform(data=shipment_info)

        if form.validate_on_submit():
            form_information = {
                "status": form.status.data,
                "tracking_number": form.tracking_number.data,
                "comments": form.comments.data,
                "datetime": str(
                    datetime.strptime(
                        "%s %s" % (form.date.data, form.time.data), "%Y-%m-%d %H:%M:%S"
                    )
                ),
            }
            update_response = requests.put(
                url_for("api.shipment_update_status", uuid=uuid, _external=True),
                headers=get_internal_api_header(),
                json=form_information,
            )

            if update_response.status_code == 200:
                flash("Shipment Status Successfully Updated")
            else:
                flash("We have a problem: %s" % (update_response.json()))

            return redirect(url_for("sample.shipment_view_shipment", uuid=uuid))
        return render_template(
            "sample/shipment/update_status.html", uuid=uuid, form=form
        )


@sample.route("/shipment/update_status/<uuid>/data")
@login_required
def shipment_update_status_data(uuid):
    shipment_response = requests.get(
        url_for("api.shipment_view_shipment", uuid=uuid, _external=True),
        headers=get_internal_api_header(),
    )

    return (
        shipment_response.text,
        shipment_response.status_code,
        shipment_response.headers.items(),
    )


@sample.route("/shipment/view/<uuid>/data")
@login_required
def shipment_view_shipment_data(uuid):
    shipment_response = requests.get(
        url_for("api.shipment_view_shipment", uuid=uuid, _external=True),
        headers=get_internal_api_header(),
    )
    # print('shipment_reponse: ', shipment_response.text)
    return (
        shipment_response.text,
        shipment_response.status_code,
        shipment_response.headers.items(),
    )


@sample.route("/shipment/new/", methods=["GET", "POST"])
@login_required
def shipment_new_step_one():
    sites_response = requests.get(
        url_for("api.site_home", _external=True), headers=get_internal_api_header()
    )

    if sites_response.status_code == 200:

        sites = []
        for site in sites_response.json()["content"]:
            sites.append([site["id"], "LIMBSIT-%i: %s" % (site["id"], site["name"])])

        form = SampleShipmentEventForm(sites)

        if form.validate_on_submit():

            new_shipment_response = requests.post(
                url_for("api.shipment_new_shipment", _external=True),
                headers=get_internal_api_header(),
                json={
                    "site_id": form.site_id.data,
                    "event": {
                        "comments": form.comments.data,
                        "datetime": str(
                            datetime.strptime(
                                "%s %s" % (form.date.data, form.time.data),
                                "%Y-%m-%d %H:%M:%S",
                            )
                        ),
                        "undertaken_by": form.undertaken_by.data,
                    },
                },
            )

            if new_shipment_response.status_code == 200:
                flash("Shipment successfully added")
                return redirect(url_for("sample.shipment_index"))

            else:
                # flash("Oh no.")
                flash(new_shipment_response.json()["message"])

        return render_template("sample/shipment/new/new.html", form=form)
    else:
        return sites_response.content


@sample.route("/shipment/cart/select/shipment", methods=["GET", "POST"])
def shipment_cart_select_shipment():
    sampleUUID = request.json["UUID"]
    sample_respose = requests.get(
        url_for("api.sample_view_sample", uuid=sampleUUID, _external=True),
        headers=get_internal_api_header(),
    )
    cart_response = requests.post(
        url_for(
            "api.select_record_cart_shipment",
            sample_id=sample_respose.json()["content"]["id"],
            _external=True,
        ),
        headers=get_internal_api_header(),
    )
    return jsonify(cart_response.status_code)


@sample.route("/shipment/cart/deselect/shipment", methods=["GET", "POST"])
def shipment_cart_deselect_shipment():
    sampleUUID = request.json["UUID"]
    sample_respose = requests.get(
        url_for("api.sample_view_sample", uuid=sampleUUID, _external=True),
        headers=get_internal_api_header(),
    )
    if sample_respose.status_code == 200:
        cart_response = requests.post(
            url_for(
                "api.deselect_record_cart_shipment",
                sample_id=sample_respose.json()["content"]["id"],
                _external=True,
            ),
            headers=get_internal_api_header(),
        )
        return jsonify(cart_response.status_code)
    return jsonify(sample_respose.status_code)


@sample.route("/shipment/cart/select", methods=["GET", "POST"])
def shipment_cart_select():
    sampleID = request.json["sample"]["id"]
    cart_response = requests.post(
        url_for("api.select_record_cart", sample_id=sampleID, _external=True),
        headers=get_internal_api_header(),
    )
    return jsonify(cart_response.status_code)


@sample.route("/shipment/cart/deselect", methods=["GET", "POST"])
def shipment_cart_deselect():
    sampleID = request.json["sample"]["id"]
    cart_response = requests.post(
        url_for("api.deselect_record_cart", sample_id=sampleID, _external=True),
        headers=get_internal_api_header(),
    )
    return jsonify(cart_response.status_code)