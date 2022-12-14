/*
Copyright (C) 2020 Keiron O'Shea <keo7@aber.ac.uk>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/


function view_consent_form() {
    var consent_id = $("#consent_select option:selected").val();
    var url = $("#consent_select_href").attr("href");
    $("#consent_select_href").attr("href", url.replace("%20", consent_id));
}


$(document).ready(function() {
    // $("#check-button").on("click", function() {
    //     var check_status = $("#check-status").html();
    //
    //     if (check_status == "Check") {
    //         $("#check-status").text("Uncheck");
    //         $("#check-button").removeClass("btn-success").addClass("btn-danger");
    //         $('.form-check-input').prop('checked', true);
    //     }
    //
    //     else {
    //         $("#check-status").text("Check");
    //         $("#check-button").removeClass("btn-danger").addClass("btn-success");
    //         $('.form-check-input').prop('checked', false);
    //     }
    // });


    view_consent_form();
    view_form_helper("consent_select");

    $("#consent_select").on("change", function() {
        view_form_helper("consent_select");
    });


});