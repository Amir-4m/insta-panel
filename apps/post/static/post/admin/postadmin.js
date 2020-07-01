(function ($) {
    $(document).ready(function () {
        var fromProjection = new OpenLayers.Projection("EPSG:4326");   // Transform from WGS 1984
        var toProjection = new OpenLayers.Projection("EPSG:900913"); // to Spherical Mercator Projection
        var map = $("#OpenLayers_Layer_Vector_19_svgRoot");

        function handleSuccess(data) {
            var select = $("#id_places");
            var j = 0;
            for (j; j <= select.children().length; j++) {
                select.remove('option')
            }
            var i = 0;
            for (i; i <= data.length; i++) {
                var name = data[i].name;
                var value = JSON.stringify(data[i]);
                select.append(new Option(name, value));
            }

        }


        map.click(function (event) {
            var pin = $("#OpenLayers_Layer_Vector_19_vroot");
            if (pin.children('circle')[0] !== undefined) {
                var latlong = $('#OpenLayers_Control_MousePosition_60').text();
                var [longitude, latitude] = latlong.split(', ');
                var lonlat1 = new OpenLayers.LonLat(longitude, latitude).transform(toProjection, fromProjection);
                $.ajax({
                    type: "GET",
                    url: "/post/get-location/",
                    data: {
                        latitude: lonlat1.lat,
                        longitude: lonlat1.lon
                    },
                    success: handleSuccess,
                });
            }

        });
    });
    $(document).on('formset:added', function (event, $row, formsetName) {
        console.log(event, $row, formsetName)
    });

    $(document).on('formset:removed', function (event, $row, formsetName) {
        console.log(event, $row, formsetName)
        // Row removed
    });
})(django.jQuery);









