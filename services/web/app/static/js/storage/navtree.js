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


function sap2tree(sap) {
    var sites = sap["content"];

    for (var i = 0; i < sites.length; i++) {
        var site = sites[i];
        site["text"] = `LIMBSITE-${site['id']}: ${site['name']}`;
        site["type"] = "site";
        site["children"] = site["buildings"];
        site["id"] = site["_links"]["self"]

        for (var j = 0; j < site["buildings"].length; j++) {
            var building = site["buildings"][j];
            building["text"] =`${building['name']}`;
            building["type"] = "building";
            building["children"] = building["rooms"];
            building["id"] = building["_links"]["self"]

            for (var k = 0; k < building["rooms"].length; k++) {
                var room = building["rooms"][k];
                room["text"] = `${room['name']}`;
                room["type"] = "room";
                room["id"] = room["_links"]["self"]
                room["children"] = room["storage"];

                for (var l = 0; l < room["storage"].length; l++) {
                    var storage = room["storage"][l];
                    //Test
                    //storage["text"] = "(" + `${building['name']}` + "F" + l + ") " + " " + `${storage["manufacturer"]}` ;
                    storage["text"] = `${storage["alias"]} (${storage["temp"]})`;
                    storage["type"] = "fridge";
                    storage["id"] = storage["_links"]["self"];
                    storage["children"] = storage["shelves"];

                    for (var m = 0; m < storage["shelves"].length; m++) {
                        var shelf = storage["shelves"][m];
                        shelf["text"] = `${shelf['name']}`;
                        shelf["type"] = "shelf";
                        shelf["id"] = shelf["_links"]["self"];

                    }
                    
                }
            }
            
        }

    }

    return {
        'types': {
            'home': { 'icon': 'fa fa-home' },
            'building': { 'icon': 'fa fa-home'},
            'site': { 'icon': 'fa fa-hospital' },
            'room': { 'icon': 'fa fa-door-closed' },
            'fridge': { 'icon': 'fa fa-temperature-low' },
            'shelf': { 'icon': 'fa fa-bars' },
            'box': { 'icon': 'fa fa-box' },
            'sample': { 'icon': 'fa fa-flask' },
        },
        'state': { 'key': 'storage' },
        'plugins' : ['state', 'types', 'wholerow', 'search'],
        'core': {
            'data': {
                'text': 'Show Sites',
                'type': 'home',
                'children': sites
            }
        }
    }
}

function collapse_sidebar() {
        $('#sidebar').toggleClass('active');
        $('#sidebar-collapse-icon').toggleClass('fa-chevron-left');
        $('#sidebar-collapse-icon').toggleClass('fa-chevron-right');
}

function open_sidebar() {
    $('#sidebar').toggleClass('false');
    $('#sidebar-collapse-icon').toggleClass('fa-chevron-left');
    $('#sidebar-collapse-icon').toggleClass('fa-chevron-right');
}

$(function() {

    //Function which controls button to collapse side bar/nav bar
    $('#sidebar-collapse').on('click', function () {
        collapse_sidebar();
    });

    function selectElement(element) {
        location.href=element.id;
    }
    //Below code displays nav tree
    $.get( "/storage/overview", function( data ) {
        last_selected = sessionStorage.getItem("last_selected");
        $('#jstree').jstree(sap2tree(data))
            .bind('ready.jstree', function (e, data) {
                $("#jstree").jstree("deselect_all");
                $("#jstree").jstree("select_node", last_selected);})

        $('#jstree').on("changed.jstree", function(e, data) {
            // Don't process event if not triggered by user (e.g. page state reload)
            sessionStorage.setItem("last_selected", data.selected)
            if(!data.event) { return; }

            switch (data.node.type) {
                case 'home':
                    location.href = '/storage/';
                    break;
                default:
                    selectElement(data.node);
                    break;
            }
        });

    });

});
