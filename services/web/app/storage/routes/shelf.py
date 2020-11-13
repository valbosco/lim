# Copyright (C) 2019  Keiron O'Shea <keo7@aber.ac.uk>
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

from flask import (
    redirect,
    abort,
    render_template,
    url_for,
    session,
    request,
    jsonify,
    flash,
)
from flask_login import current_user, login_required
from .. import storage
from ..forms import NewShelfForm, SampleToEntityForm, RackToShelfForm
import requests
from ...misc import get_internal_api_header
from datetime import datetime

@storage.route("/coldstorage/LIMBCS-<id>/shelf/new", methods=["GET", "POST"])
@login_required
def new_shelf(id):
        
    response = requests.get(
        url_for("api.storage_coldstorage_view", id=id, _external=True),
        headers=get_internal_api_header()
    )

    if response.status_code == 200:
        form = NewShelfForm()

        if form.validate_on_submit():

            new_response = requests.post(
                url_for("api.storage_shelf_new", _external=True),
                headers=get_internal_api_header(),
                json = {
                    "name": form.name.data,
                    "description": form.description.data,
                    "storage_id": id
                }
            )

            if new_response.status_code == 200:
                flash("Shelf Successfully Created")
                # TODO: Replace.
                return redirect(url_for("document.index"))
            return abort(new_response.status_code)
        
        return render_template("storage/shelf/new.html", form=form, cs=response.json()["content"])
    
    return abort(response.status_code)

@storage.route("/shelf/LIMBSHF-<id>", methods=["GET"])
@login_required
def view_shelf(id):
    response = requests.get(
        url_for("api.storage_shelf_view", id=id, _external=True),
        headers=get_internal_api_header()
    )

    if response.status_code == 200:
        return render_template("storage/shelf/view.html", shelf=response.json()["content"])

    return abort(response.status_code)

@storage.route("/shelf/LIMBSHF-<id>/assign_rack", methods=["GET", "POST"])
@login_required
def assign_rack_to_shelf(id):
    response = requests.get(
        url_for("api.storage_shelf_view", id=id, _external=True),
        headers=get_internal_api_header()
    )

    if response.status_code == 200:
        
        rack_response = requests.get(
            url_for("api.storage_rack_home", _external=True),
            headers=get_internal_api_header()
        )

        if rack_response.status_code == 200:
            
            form = RackToShelfForm(rack_response.json()["content"])

            if form.validate_on_submit():
                rack_move_response = requests.post(
                    url_for("api.storage_transfer_rack_to_shelf", _external=True),
                    headers=get_internal_api_header(),
                    json={
                        "rack_id": form.racks.data,
                        "shelf_id": id,
                        "entry_datetime": str(datetime.strptime(
                            "%s %s" % (form.date.data, form.time.data),
                            "%Y-%m-%d %H:%M:%S"
                        )),
                        "entry": form.entered_by.data
                        }
                )

                if rack_move_response.status_code == 200:
                    return redirect(url_for("storage.view_shelf", id=id))

                return abort(rack_response.status_code)

            return render_template("storage/shelf/rack_to_shelf.html", shelf=response.json()["content"], form=form)
    
    return abort(response.status_code)


@storage.route("/shelf/LIMBSHF-<id>/assign_sample", methods=["GET", "POST"])
@login_required
def assign_sample_to_shelf(id):
    response = requests.get(
        url_for("api.storage_shelf_view", id=id, _external=True),
        headers=get_internal_api_header()
    )

    if response.status_code == 200:
        
        sample_response = requests.get(
            url_for("api.sample_home", _external=True),
            headers=get_internal_api_header()
        )

        if sample_response.status_code == 200:

            form = SampleToEntityForm(sample_response.json()["content"])

            if form.validate_on_submit():
              
                sample_move_response = requests.post(
                    url_for("api.storage_transfer_sample_to_shelf", _external=True),
                    headers=get_internal_api_header(),
                    json={
                        "sample_id": form.samples.data,
                        "shelf_id": id,
                        "entry_datetime": str(datetime.strptime(
                            "%s %s" % (form.date.data, form.time.data),
                            "%Y-%m-%d %H:%M:%S"
                        )),
                        "entry": form.entered_by.data
                        }
                )

                if sample_move_response.status_code == 200:
                    return "Hello World"

                else:
                    flash(sample_move_response.json())

            return render_template("storage/shelf/sample_to_shelf.html", shelf=response.json()["content"], form=form)

    return abort(response.status_code)