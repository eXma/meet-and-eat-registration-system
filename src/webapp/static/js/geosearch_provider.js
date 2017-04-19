/**
 * Created with IntelliJ IDEA.
 * User: jan
 * Date: 16.02.13
 * Time: 08:43
 * To change this template use File | Settings | File Templates.
 */


/**
 * L.Control.GeoSearch - search for an address and zoom to it's location
 * L.GeoSearch.Provider.OpenStreetMap uses openstreetmap geocoding service
 * https://github.com/smeijer/leaflet.control.geosearch
 */

L.GeoSearch.Provider.OpenStreetMap = L.Class.extend({
    options: {

    },

    initialize: function (options) {
        options = L.Util.setOptions(this, options);
    },

    GetServiceUrl: function (street, number, city) {
        var parameters = L.Util.extend({
            street: encodeURIComponent(number + " " + street),
            city: encodeURIComponent(city),
            country: encodeURIComponent("Germany"),
            format: 'json'
        }, this.options);

        return 'https://nominatim.openstreetmap.org/search'
            + L.Util.getParamString(parameters);
    },

    ParseJSON: function (data) {
        if (data.length == 0)
            return [];

        var results = [];
        for (var i = 0; i < data.length; i++)
            results.push(new L.GeoSearch.Result(
                data[i].lon,
                data[i].lat,
                data[i].display_name
            ));

        return results;
    }
});


/**
 * L.Control.GeoSearch - search for an address and zoom to it's location
 * L.GeoSearch.Provider.Google uses google geocoding service
 * https://github.com/smeijer/leaflet.control.geosearch
 */

onLoadGoogleApiCallback = function () {
    L.GeoSearch.Provider.Google.Geocoder = new google.maps.Geocoder();
};

L.GeoSearch.Provider.Google = L.Class.extend({
    options: {

    },

    initialize: function (options) {
        options = L.Util.setOptions(this, options);

        $.ajax({
            url: "https://maps.googleapis.com/maps/api/js?v=3&callback=onLoadGoogleApiCallback&sensor=false",
            dataType: "script"
        });
    },

    GetLocations: function (qry, callback) {
        var geocoder = L.GeoSearch.Provider.Google.Geocoder;

        var parameters = L.Util.extend({
            address: qry
        }, this.options);

        var results = geocoder.geocode(parameters, function (data) {
            data = {results: data};

            if (data.results.length == 0)
                return [];

            var results = [];
            for (var i = 0; i < data.results.length; i++)
                results.push(new L.GeoSearch.Result(
                    data.results[i].geometry.location.lng(),
                    data.results[i].geometry.location.lat(),
                    data.results[i].formatted_address
                ));

            if (typeof callback == 'function')
                callback(results);
        });
    }
});
