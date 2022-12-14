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

from .models import Event
import marshmallow_sqlalchemy as masql
from ..extensions import ma
from ..auth.views import BasicUserAccountSchema, UserAccountSearchSchema


class NewEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Event

    datetime = masql.auto_field()
    undertaken_by = masql.auto_field()
    comments = masql.auto_field()


new_event_schema = NewEventSchema()


class EventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Event

    id = masql.auto_field()
    datetime = masql.auto_field()
    undertaken_by = masql.auto_field()
    comments = masql.auto_field()
    # author = ma.Nested(BasicUserAccountSchema, many=False)
    author = ma.Nested(UserAccountSearchSchema, many=False)
    created_on = masql.auto_field()


event_schema = EventSchema()
events_schema = EventSchema(many=True)
