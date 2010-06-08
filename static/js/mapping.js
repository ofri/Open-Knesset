
/*
 Creates a google map in map_container, and creates markers for all locations in locations_list.
 A single location is an object with the following members:
    lat: latitude
    lng: longtitude
    text: on over text for the marker (optional)
*/
function create_locations_map(map_container, locations_list) {
    if (GBrowserIsCompatible()) {
	   var copyOSM = new google.maps.CopyrightCollection("<a href=\"http://www.openstreetmap.org/\">OpenStreetMap</a>");
	   copyOSM.addCopyright(new google.maps.Copyright(1, new google.maps.LatLngBounds(new google.maps.LatLng(-90,-180), new google.maps.LatLng(90,180)), 0, " "));

	   var tilesMapnik     = new google.maps.TileLayer(copyOSM, 1, 17, {tileUrlTemplate: 'http://tile.openstreetmap.org/{Z}/{X}/{Y}.png'});
	   var mapMapnik     = new google.maps.MapType([tilesMapnik],
												   G_NORMAL_MAP.getProjection(),
												   "מפת רחובות",
												   { maxResolution: 18 });
	   var mapSatellite  = new google.maps.MapType(G_SATELLITE_MAP.getTileLayers(),
												   G_SATELLITE_MAP.getProjection(),
												   "תמונת לווין");
	   var map           = new google.maps.Map2(map_container, { mapTypes: [ mapMapnik,mapSatellite ] });
	   //var map = new GMap2(map_container);
        /*map.setCenter(new GLatLng(37.4419, -122.1419), 13);*/

	   $(window).unload(function() {
					   GUnload();
	   });
    }
}
