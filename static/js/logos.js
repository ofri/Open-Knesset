(function ($) {
    $.fn.hLogo = function (step) {
        step = typeof(step)=='undefined'?0:step;
        var ctx = this[0].getContext('2d');
        var r = this.width()*4/10;
        var edge = Math.PI/13;  /* size of half a typical's line edge in radians */
        var base = edge*3;      /* size of half of the base in radians */
        var innerCircle = Math.ceil(r/4);  /* radius of the inner circle in pixels */

        /* move our center to the circle's center */
        ctx.save();
        ctx.translate(r,r);
        /* by using rotate, we can keep working around angle 0 */
        ctx.rotate(Math.PI*2*step/7 +Math.PI/2);
        /* basic setup, line and fill color and line width */
        ctx.strokeStyle = "rgb(37,64,123)";  
        ctx.fillStyle = "rgb(37,64,123)";  
        ctx.lineWidth = Math.ceil(r/7);
        /* draw the base */
        ctx.beginPath();
        ctx.moveTo(0,0);
        ctx.lineTo(r, 0);
        ctx.stroke();
        ctx.beginPath();
        with (Math) {
            ctx.moveTo(r*cos(base), r*sin(base));
            ctx.lineTo(r*cos(-base), r*sin(-base));
        }
        ctx.arc(0,0, r, -base, base, false);
        ctx.fill();
        ctx.rotate(Math.PI/3);
        /* drawing the branches */
        for (var i=0;i<7;i++) {
            ctx.beginPath();
            ctx.moveTo(r,0);
            ctx.lineTo(0, 0);
            ctx.stroke();
            ctx.beginPath();
            with (Math) {
                ctx.moveTo(r*cos(edge), r*sin(edge));
                ctx.quadraticCurveTo(ceil(r*0.5), 0, r*cos(-edge), r*sin(-edge));
                ctx.arc(0,0, r, -edge, edge, false);
            }
            ctx.fill();
            ctx.rotate(Math.PI/4.5);
        }
        ctx.beginPath();
        ctx.arc(0,0, innerCircle, 0, Math.PI*2, false);
        ctx.fill();
        ctx.restore();
        
    };
})(jQuery);

