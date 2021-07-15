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


import requests
from ...misc import get_internal_api_header
from .. import storage
from flask import render_template, redirect, url_for, abort, flash
from flask_login import current_user, login_required
from ..forms import BuildingRegistrationForm


@storage.route("site/LIMBSITE-<id>/new_building", methods=["GET", "POST"])
@login_required
def new_building(id):

    response = requests.get(
        url_for("api.site_view", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if response.status_code == 200:
        form = BuildingRegistrationForm()

        if form.validate_on_submit():
            post_response = requests.post(
                url_for("api.storage_building_new", _external=True),
                headers=get_internal_api_header(),
                json={"site_id": id, "name": form.name.data},
            )

            if post_response.status_code == 200:
                flash("Building Successfully Created")
                return redirect(
                    url_for(
                        "storage.view_building",
                        id=post_response.json()["content"]["id"],
                    )
                )
            else:
                return abort(response.status_code)

        return render_template(
            "storage/building/new.html", form=form, site=response.json()["content"]
        )

    abort(response.status_code)


@storage.route("/building/LIMBUILD-<id>", methods=["GET"])
@login_required
def view_building(id):
    response = requests.get(
        url_for("api.storage_building_view", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if response.status_code == 200:
        return render_template(
            "storage/building/view.html", building=response.json()["content"]
        )

    return abort(response.status_code)


@storage.route("/building/LIMBUILD-<id>/edit", methods=["GET", "POST"])
@login_required
def edit_building(id):

    response = requests.get(
        url_for("api.storage_building_view", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if response.status_code == 200:

        form = BuildingRegistrationForm(data=response.json()["content"])

        if form.validate_on_submit():
            form_information = {
                "name": form.name.data,
            }

            edit_response = requests.put(
                url_for("api.storage_edit_building", id=id, _external=True),
                headers=get_internal_api_header(),
                json=form_information,
            )

            if edit_response.status_code == 200:
                flash("Building Successfully Edited")
            else:
                flash("We have a problem: %s" % (edit_response.json()))

            return redirect(url_for("storage.view_building", id=id))

        return render_template(
            "storage/building/edit.html", building=response.json()["content"], form=form
        )

    return abort(response.status_code)


@storage.route("/buildings/LIMBBUILD-<id>/delete", methods=["GET", "POST"])
@login_required
def delete_building(id):

    edit_response = requests.put(
        url_for("api.storage_building_delete", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if edit_response.status_code == 200:
        flash("Building Successfully Deleted")
    else:
        flash("We have a problem: %s" % (id))

    # return redirect(url_for("storage.view_site",id=edit_response.json()["content"], _external=True))
    return redirect(url_for("storage.index",_external=True))

# @storage.route("/buildings/LIMBBUILD-<id>/delete", methods=["GET", "POST"])
# @login_required
# def delete_building(id):
#     #confirmation = requests.put(url_for("api.storage_building_delete_confirmation",id=id,_external=True))
#
#     response = requests.get(
#         url_for("api.storage_building_view", id=id, _external=True),
#         headers=get_internal_api_header(),
#     )
#
#     if response.status_code == 200:
#
#         form = DeleteForm(data=response.json()["content"])
#
#         if form.validate_on_submit():
#             edit_response = requests.put(
#                 url_for("api.storage_building_delete", id=id, _external=True),
#                 headers=get_internal_api_header(),
#             )
#
#             if edit_response.status_code == 200:
#                 flash("Building Successfully Deleted")
#             else:
#                 flash("We have a problem: %s" % (id))
#
#         # return redirect(url_for("storage.view_site",id=edit_response.json()["content"], _external=True))
#             return redirect(url_for("storage.index",_external=True))
#     else:
#         flash("We have a problem:")
#     return abort(response.status_code)


