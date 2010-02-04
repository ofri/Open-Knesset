function try_to_fix_facebook(){
//    alert('x');
    var x = $('#FB_HiddenContainer');
    if (x === undefined){
        var t=setTimeout(function(){try_to_fix_facebook();},1000);
    } else {
        $('#FB_HiddenContainer').css('left', "50%");
    };
};

$(document).ready(try_to_fix_facebook);
