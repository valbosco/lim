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

from ...extensions import ma
from ...database import Donor
from ..enums import RaceTypes, BiologicalSexTypes, DonorStatusTypes

from sqlalchemy_continuum import version_class, parent_class
from ...extensions import ma
import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField

from ...auth.views import BasicUserAccountSchema
from ..enums import BiologicalSexTypes, DonorStatusTypes, RaceTypes
from ...sample.enums import Colour

from .diagnosis import DonorDiagnosisEventSchema


class DonorSearchSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Donor

    id = masql.auto_field()
    uuid = masql.auto_field()
    sex = EnumField(BiologicalSexTypes, by_value=True)
    status = EnumField(DonorStatusTypes, by_value=True)
    race = EnumField(RaceTypes, by_value=True)
    colour = EnumField(Colour, by_value=True)


class DonorSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Donor

    id = masql.auto_field()

    uuid = masql.auto_field()

    dob = ma.Date()

    sex = EnumField(BiologicalSexTypes, by_value=True)
    status = EnumField(DonorStatusTypes, by_value=True)
    death_date = ma.Date()

    weight = masql.auto_field()
    height = masql.auto_field()

    diagnoses = ma.Nested(DonorDiagnosisEventSchema, many=True)

    race = EnumField(RaceTypes, by_value=True)

    author = ma.Nested(BasicUserAccountSchema)
    updater = ma.Nested(BasicUserAccountSchema)
    colour = EnumField(Colour, by_value=True)

    created_on = ma.Date()
    updated_on = ma.Date()

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("donor.view", id="<id>", _external=True),
            "collection": ma.URLFor("donor.index", _external=True),
            "edit": ma.URLFor("donor.edit", id="<id>", _external=True),
            "assign_diagnosis": ma.URLFor(
                "donor.new_diagnosis", id="<id>", _external=True
            ),
        }
    )


donor_schema = DonorSchema()
donors_schema = DonorSchema(many=True)


class NewDonorSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Donor

    dob = ma.Date()
    sex = EnumField(BiologicalSexTypes)
    status = EnumField(DonorStatusTypes)
    death_date = ma.Date()
    colour = EnumField(Colour)
    mpn = masql.auto_field()
    enrollment_site_id = masql.auto_field()
    registration_date = masql.auto_field()

    weight = masql.auto_field()
    height = masql.auto_field()

    race = EnumField(RaceTypes)


new_donor_schema = NewDonorSchema()
