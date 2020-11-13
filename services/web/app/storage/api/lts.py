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


from flask import request, current_app, jsonify, send_file
from ...api import api
from ...api.responses import *
from ...api.filters import generate_base_query_filters, get_filters_and_joins
from ...decorators import token_required
from ...webarg_parser import use_args, use_kwargs, parser

from marshmallow import ValidationError

from ...database import db, UserAccount, ColdStorage

from ..views import *


@api.route("/storage/coldstorage", methods=["GET"])
@token_required
def storage_coldstorage_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_cold_storages_schema.dump(ColdStorage.query.all())
    )


@api.route("/storage/coldstorage/LIMBCS-<id>", methods=["GET"])
@token_required
def storage_coldstorage_view(id, tokenuser: UserAccount):
    return success_with_content_response(
        cold_storage_schema.dump(
            ColdStorage.query.filter_by(id=id).first_or_404()
        )
    )


@api.route("/storage/coldstorage/new", methods=["POST"])
@token_required
def storage_coldstorage_new(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        cs_result = new_cold_storage_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    cs = ColdStorage(**cs_result)
    cs.author_id = tokenuser.id

    try:
        db.session.add(cs)
        db.session.commit()

        return success_with_content_response(basic_cold_storage_schema.dump(cs))
    except Exception as err:
        return transaction_error_response(err)


@api.route("/storage/coldstorage/LIMBCS-<id>/edit", methods=["PUT"])
@token_required
def storage_coldstorage_edit(id, tokenuser: UserAccount):

    cs = ColdStorage.query.filter_by(id=id).first()

    if not room:
        return not_found()

    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        result = new_cold_storage_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    for attr, value in values.items():
        setattr(cs, attr, value)

    cs.editor_id = tokenuser.id

    try:
        db.session.add(cs)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(basic_cold_storage_schema.dump(cs))
    except Exception as err:
        return transaction_error_response(err)


@api.route("/storage/coldstorage/LIMBCS-<id>/lock", methods=["PUT"])
@token_required
def storage_coldstorage_lock(id, tokenuser: UserAccount):

    cs = ColdStorage.query.filter_by(id=id).first()

    if not cs:
        return not_found()

    cs.is_locked = not cs.is_locked
    cs.editor_id = tokenuser.id

    db.session.add(cs)
    db.session.commit()
    db.session.flush()

    return success_with_content_response(basic_cold_storage_schema.dump(cs))