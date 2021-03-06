/*
Flot plugin that adds some image cursors that can move along the path
*/

(function ($) {
    var options = {
        markers: []
    }

    function addOptions(plot, globals) {
        if (typeof(globals.markers) != undefined) {
            options.markers = globals.markers;
        }
    }

    function addImageMarkers(plot, ctx) {
        var xaxis = plot.getAxes().xaxis;
        var yaxis = plot.getAxes().yaxis;

        for (var i in options.markers) {
            var series = plot.getData()[0];
            var points = series.datapoints.points;
            var marker = options.markers[i];
            var oldPos = null;
            var rad = 0;

            var x = xaxis.p2c(marker.x) + plot.getPlotOffset().left;
            var y = yaxis.p2c(marker.y) + plot.getPlotOffset().top;

            if (typeof(marker.queue) == "undefined")
                marker.queue = []
            if (marker.queue.length > 10)
                oldPos = marker.queue.shift()
            marker.queue.push({x: x, y: y});

            if (oldPos != null) {
                var movedX = Math.abs(x-oldPos.x);
                var movedY = y-oldPos.y;
                if (movedX > 0) {
                    rad = Math.atan(movedY/movedX);
                }
            }

            ctx.save();
            ctx.translate(x, y);
            ctx.rotate(rad);
            ctx.drawImage(marker.image, -16, -16, 32, 32);
            ctx.restore();
        }
    }
    
    function init(plot) {
        plot.hooks.drawOverlay.push(addImageMarkers);
        plot.hooks.processOptions.push(addOptions);
        plot.updateMarker = function (x, y, player) {
            options.markers[parseInt(player)].x = parseFloat(x);
            options.markers[parseInt(player)].y = parseFloat(y);
            plot.triggerRedrawOverlay();
        }
    }
    
    $.plot.plugins.push({
        init: init,
        name: 'imagemarkers',
        version: '1.0',
        options: options
    });
})(jQuery);
