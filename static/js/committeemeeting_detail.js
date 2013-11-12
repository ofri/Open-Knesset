function hide_annotation_form(annoid) {
    $("#annotationform-"+annoid).hide();
    $("#annotations-"+annoid).show();
    $("#selectable-"+annoid).text(gettext("Annotate"));
    $("#annotationrealform-"+annoid)[0].reset();
    $("#editable-"+annoid).show();
    if(annotation_objects[annoid].annotation_count >0){
      $("#annotationtoolbox-"+annoid).show();
    }
}
$(function(){
    var options_bill = { 
         serviceUrl:'/bill/auto_complete/',
         minChars:2, 
         maxHeight:400,
         width:400,
         deferRequestBy: 100, //miliseconds
         onSelect: function(value, data, me){ 
            me.siblings("input[name$='bill_id']").val(data);
            me.siblings("input[type$='submit']").removeAttr('disabled'); },
         };

    var options_mk = { 
         serviceUrl:'/member/auto_complete/',
         minChars:0, 
         maxHeight:400,
         width:150,
         deferRequestBy: 100, //miliseconds
         };

    $('input.bill_input').autocomplete(options_bill);
    $('input.bill_input').keydown(function() { 
        $(this).siblings("input[name$='bill_id']").val('');
        $(this).siblings("input[type$='submit']").attr('disabled', 'disabled'); });
    $("input[name$='mk_name']").autocomplete(options_mk);

    $(".annotation-content").each(function(){
        var annoid = $(this).attr("id").split("-")[1];
        annotation_objects[annoid] = new Annotations(annoid);
    });
    for(var a in annotation_objects){
        annotation_objects[a].importQuotes();
        annotation_objects[a].insertQuotes();
    }
    $(".annotationform-link").click(function(e){
      e.preventDefault();
      if (!window.logged_in) {
          var msg = gettext("Sorry, only logged users can annotate.");
          $.jGrowl(msg, {sticky: true});
          return false
      }
      if (!window.permission) {
          var msg = $("#message_permission").html()
          $.jGrowl(msg, {sticky: true});
          return false
      }

      var annoid = $(this).attr("id").split("-")[1];
      annotation_objects[annoid].toggleSelectView();
      if($("#annotations-"+annoid).css("display")=="none"){
        hide_annotation_form(annoid);
      } else{
        if (!$("#annotationform-"+annoid).length) {
            var speech_part = {id: annoid, length: window.parts_lengths[annoid] };
            $("#annotations-"+annoid).before(tmpl("annotationform", {speech_part: speech_part}))
            $(".annotationform-cancel").click(function(e) {
                e.preventDefault();
                var annoid = $(this).attr("id").split("-")[1];
                annotation_objects[annoid].toggleSelectView();
                hide_annotation_form(annoid);
            });
          $("#annotationrealform-"+annoid).submit(function(e){
            var id = $(this).attr("id").split("-")[1];
            if($("#selection_start-"+id).val()=="" || $("#selection_end-"+id).val()==""){
              alert(gettext("Please make a selection."));
              e.preventDefault();
              return false;
            }
            return true;
          });
            $('input[name=color]').colorPicker();
        }
        else
            $("#annotationform-"+annoid).show();
        $(this).text(gettext("Cancel"));
        $("#annotations-"+annoid).hide();
        $("#editable-"+annoid).hide();
        $("#annotationtoolbox-"+annoid).hide();
      }
    });
  $(".markall").click(function(e){
    var aid = $(this).attr("id").split("-")[1];
    if($(this).attr('checked')){
      annotation_objects[aid].updateDefaultAnnotationColor("self");
    } else{
      annotation_objects[aid].updateDefaultAnnotationColor("inherit");
    }
  });
  $(".reallydelete").live("submit", function(e){
    var anno_id = $(this).children('[name=annotation_id]').val();
    var username = $('#annotation-'+anno_id+' a.user-link').html();

    if (!window.is_staff && username != window.username){
        var msg = $("#message_staff").html()
        $.jGrowl(msg, {sticky: true});
        return false
    }
    return confirm(gettext('Delete can not be un-done. Are you sure?'));
  });
  $(".annotationflagselect").change(function(e){
    var id = $(this).parents("form").attr("id").split("-")[1];
    var val = parseInt($(this).val());
    var color = null;
    switch(val){
      case 0: // Put more colors here
        color = "#99ccff"; break;
    }
    if(color != null){
      $("#color_value").val(color);
      $("#annotationcolor-"+id).val(color);
      $("div.color_picker").css("background-color", color); 
    }
  });
  $(".toggle").live("click", function(e){
     e.preventDefault();
     var id = $(this).attr("id");
     if (id == ""){
       var url = $(this).attr("href");
       var sel = $("."+url.substring(1,url.length)+"-container");
     } else {var sel = $("#"+id+"-container");}
     sel.toggle();
  });

    /** infinite scroll **/

    (function(){
        var _isFloat = false;
        var _isFooterVisible = false;

        var _isActive = function() {
            return ($(window).width() > 1200 && $(window).height() > 500);
        };

        var _float = function() {
            $('#app-header').css({
                'position' : 'fixed',
                'top' : '0',
                'left' : 0,
                'margin' : 0,
                'padding-left' : $('#app-header').css('margin-left'),
                'padding-right' : $('#app-header').css('margin-right'),
                'z-index' : '999',
                'background' : $('body').css('background')
            });
            $('#app-header .row').hide();
            $('section.container > ul.breadcrumb').css({
                'position' : 'fixed',
                'top' : $('#app-header').height() + 'px',
                'padding-top':'5px',
                'z-index' : '950',
                'background' : $('body').css('background'),
                'width' : '100%',
                'margin-right' : '-10px'
            })
            var headerHeight = $('section.container > ul.breadcrumb').height() + $('#app-header').height() + 25;
            $('#content-main > div > div.row > div.span3').css({
                'position' : 'fixed',
                'top' : headerHeight+'px',
                'left' : $('#content-main > div > div.row > div.span3').position().left + 'px',
                'height' : ($.waypoints('viewportHeight') - headerHeight - 5) + 'px',
                'overflow' : 'auto'
            });
        };

        var _unfloat = function() {
            $('#content-main > div > div.row > div.span3').removeAttr('style');
            $('#app-header').removeAttr('style');
            $('#app-header .row').show();
            $('section.container > ul.breadcrumb').removeAttr('style');
        };

        var _onProtocolWaypoint = function(direction) {
            if (!_isFooterVisible && _isActive()) {
                if (direction == 'down' && !_isFloat) {
                    _float();
                    _isFloat = true;
                } else if (direction == 'up' && _isFloat) {
                    _unfloat();
                    _isFloat = false;
                };
            };
        };

        var _onFooterWaypoint = function(direction) {
            if (direction == 'down') {
                _isFooterVisible = true;
                if (_isFloat && _isActive()) {
                    _unfloat();
                };
            } else {
                _isFooterVisible = false;
                if (_isFloat && _isActive()) {
                    _float();
                };
            };
        };

        var _onWindowResize = function() {
            if (_isActive()) {
                if (!_isFooterVisible && _isFloat) {
                    _unfloat();
                    _float();
                };
            } else {
                if (!_isFooterVisible && _isFloat) {
                    _unfloat();
                    _isFloat = false;
                }
            };
        };

        $('#app-footer').waypoint(_onFooterWaypoint, {offset: '130%'});
        $('.protocol').waypoint(_onProtocolWaypoint, {offset: -50});
        $(window).resize(_onWindowResize);

    })();

});
