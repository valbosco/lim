# Copyright (C) 2020  Keiron O'Shea <keo7@aber.ac.uk>
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

from flask import request, abort, url_for
from marshmallow import ValidationError
from ...api import api, generics
from ...api.responses import *
from .base import func_update_sample_status
from ...decorators import token_required
from ...misc import get_internal_api_header

from ..views import new_sample_review_schema, sample_review_schema, new_sample_disposal_schema, new_sample_schema

from ..enums import SampleStatus, ReviewType, ReviewResult, SampleQuality, DisposalInstruction
from ...database import db, Sample, SampleReview, SampleDisposal, UserAccount, Event
from sqlalchemy.sql import func


@api.route("/sample/review/<uuid>/edit", methods=["POST"])
@token_required
def sample_edit_sample_review(uuid, tokenuser: UserAccount):
    pass

@api.route("/sample/review/<uuid>/remove", methods=["POST"])
@token_required
def sample_remove_sample_review(uuid, tokenuser: UserAccount):
    review_event = SampleReview.query.filter_by(uuid=uuid).first()
    print("review_event: ", review_event)
    if not review_event:
        return not_found("review event")

    # Collection of all relevant records
    sample = Sample.query.filter_by(id=review_event.sample_id).first()
    if not sample:
        return not_found("Sample")

    if sample.is_locked:
        return locked_response("Sample")

    sample_uuid = sample.uuid
    print('uuid', sample_uuid)
    disposal_instruction = SampleDisposal.query.filter_by(review_event_id=review_event.id).first()
    print('disposal_instruction', disposal_instruction)
    event = Event.query.filter_by(id=review_event.event_id).first()
    print('event', event)

    if disposal_instruction:
        if disposal_instruction.approved is not None:
            return in_use_response("approved/rejected disposal instruction")

        if sample.disposal_id:
            if sample.disposal_id == disposal_instruction.id:
                sample.disposal_id = None
                db.session.add(sample)
                db.session.flush()

        try:
            db.session.delete(disposal_instruction)
            db.session.flush()

        except Exception as err:
            return transaction_error_response(err)

    try:
        db.session.delete(review_event)
        db.session.flush()
        if event:
            db.session.delete(event)
        db.session.commit()
        message = "Review/disposal instruction successfully deleted! "
    except Exception as err:
        return transaction_error_response(err)

    # Update sample status
    res = func_update_sample_status(tokenuser=tokenuser, auto_query=True, sample=sample,
                 events={"sample_disposal": None, "sample_review": None})

    print("sample", sample, res["message"])
    if res["success"]:
        if res["sample"]:
            try:
                db.session.add(sample)
                db.session.commit()
                #return success_with_content_response(sample_uuid)
                return success_with_content_message_response(sample_uuid, message=message + res["message"])

            except Exception as err:
                return success_with_content_message_response(sample_uuid,
                       message=message + "Transaction error in sample status update")

    return success_with_content_message_response(sample_uuid, message=message + res["message"])


@api.route("/sample/new/review_disposal", methods=["POST"])
@token_required
def sample_new_sample_review_disposal(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    print("values: ", values)
    sample = Sample.query.filter_by(id=values["sample_id"]).first_or_404()
    disposal_id = sample.disposal_id
    disposal_info = None
    if "disposal_info" in values:
        disposal_info = values.pop("disposal_info")
        disposal_info["sample_id"] = sample.id

    try:
        sample_review_values = new_sample_review_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    if disposal_info:
        try:
            results = new_sample_disposal_schema.load(disposal_info)
        except ValidationError as err:
            return validation_error_response(err)

    new_event = Event(
        datetime=sample_review_values["event"]["datetime"],
        undertaken_by=sample_review_values["event"]["undertaken_by"],
        comments=sample_review_values["event"]["comments"],
        author_id=tokenuser.id,
    )

    try:
        db.session.add(new_event)
        db.session.flush()
        print("new_event.id: ", new_event.id)
    except Exception as err:
        return transaction_error_response(err)


    new_sample_review = SampleReview(
        result=sample_review_values["result"],
        review_type=sample_review_values["review_type"],
        sample_id=sample.id,
        quality=sample_review_values["quality"],
        author_id=tokenuser.id,
        event_id=new_event.id,
    )
    try:
        db.session.add(new_sample_review)
        db.session.flush()
        print("new_review.id: ", new_sample_review.id)
    except Exception as err:
        return transaction_error_response(err)

    sample_status_events = {"sample_review": new_sample_review}

    if disposal_info:
        # Add new disposal instruction
        # TODO: check workflow: Update if existing instruction hasn't been approved?
        new_instruction = True
        # if disposal_id:
        #     disposal_instruction = SampleDisposal.query.filter_by(id=disposal_id).\
        #                        first_or_404()
        #     if disposal_instruction:
        #         if not disposal_instruction.approval_event_id:
        #             new_instruction = False

        if new_instruction:
            disposal_instruction = SampleDisposal(**disposal_info)
            disposal_instruction.review_event_id = new_sample_review.id
            disposal_instruction.author_id = tokenuser.id

        # else:
        #     disposal_instruction.update(disposal_info)
        #     disposal_instruction.review_event_id = new_sample_review.id
        #     disposal_instruction.editor_id = tokenuser.id
        #     disposal_instruction.updated_on = func.now()

        try:
            db.session.add(disposal_instruction)
            db.session.flush()
            print("disposal_id: ", disposal_instruction.id)
        except Exception as err:
            return transaction_error_response(err)

        sample_status_events["sample_disposal"] = disposal_instruction
        # Update sample status
        # sample.disposal_id = disposal_instruction.id
        # if disposal_instruction.instruction == DisposalInstruction.REV:
        #     # Pending review
        #     sample.status = "NRE"

    ####  Update sample status
    # IF review failed: set status to unusable for purity/quantity test
    #                   and missing for identity test,
    # IF pass: only set status to available if the review and quality is good
    #                   otherwise Unusable or Further Review Pending
    # if new_sample_review.result == ReviewResult.FA:
    #     if new_sample_review.review_type == ReviewType.IC:
    #         print('Id check!')
    #         sample.status = SampleStatus.MIS
    #     else:
    #         sample.status = SampleStatus.UNU
    # elif new_sample_review.result == ReviewResult.PA:
    #     print('pass!')
    #     if new_sample_review.quality == SampleQuality.GOO:
    #         sample.status = SampleStatus.AVA
    #     elif new_sample_review.quality == SampleQuality.NOT:
    #         sample.status = SampleStatus.NRE
    # else:
    #     sample.status = SampleStatus.UNU
    #
    # sample.editor_id = tokenuser.id
    # sample.update_on = func.now()

    # Update sample status
    res = func_update_sample_status(tokenuser=tokenuser, auto_query=True, sample=sample, events=sample_status_events)
                 #events={"sample_disposal": disposal_instruction, "review_event": None})

    message = "Review/disposal instruction successfully added! " + res["message"]
    print("sample", sample, res["message"])

    try:
        if res["success"] is True and res["sample"]:
            db.session.add(sample)

        db.session.commit()
        return success_with_content_message_response(
            sample_review_schema.dump(new_sample_review), message
        )

    except Exception as err:
        return transaction_error_response(err)

    # try:
    #     db.session.add(sample)
    #     db.session.commit()
    #
    #     return success_with_content_response(
    #         sample_review_schema.dump(new_sample_review)
    #     )
    # except Exception as err:
    #     return transaction_error_response(err)


# not updating sample status or disposal instruction
@api.route("/sample/new/review", methods=["POST"])
@token_required
def sample_new_sample_review(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        sample_review_values = new_sample_review_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_event = Event(
        datetime=sample_review_values["event"]["datetime"],
        undertaken_by=sample_review_values["event"]["undertaken_by"],
        comments=sample_review_values["event"]["comments"],
        author_id=tokenuser.id,
    )

    try:
        db.session.add(new_event)
        db.session.commit()
        db.session.flush()
    except Exception as err:
        return transaction_error_response(err)

    sample = Sample.query.filter_by(id=values["sample_id"]).first_or_404()

    new_sample_review = SampleReview(
        result=sample_review_values["result"],
        review_type=sample_review_values["review_type"],
        sample_id=sample.id,
        quality=sample_review_values["quality"],
        author_id=tokenuser.id,
        event_id=new_event.id,
    )

    try:
        db.session.add(new_sample_review)
        db.session.add(sample)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(
            sample_review_schema.dump(new_sample_review)
        )
    except Exception as err:
        return transaction_error_response(err)
