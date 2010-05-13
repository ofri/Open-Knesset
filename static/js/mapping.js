
/*
 Creates a google map in map_container, and creates markers for all locations in locations_list.
 A single location is an object with the following members:
    lat: latitude
    lng: longtitude
    text: on over text for the marker (optional)
*/
function create_locations_map(map_container, locations_list) {
    if (GBrowserIsCompatible()) {
        var map = new GMap2(map_container);
        /*map.setCenter(new GLatLng(37.4419, -122.1419), 13);*/

        $(window).unload(function() {
            GUnload();
        });
    }
}
