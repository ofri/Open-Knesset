var selected_tags = {};
var current_id = "";
var current_object_type = "";
var current_app = "";

function get_tags_list() {
    $("#possible_tags").html('');
    $.ajax({url: '/api/tag/', success: get_tags_list_callback, cache: false});
}

function get_tags_list_callback(data) {
    $.each(data, function(i,item){
            var href = "javascript:toggle_tag("+item.id+");";
            $('<a class="tag">').attr("id", "possible_tag_"+item.id).attr("href", href).html(item.name).appendTo("#possible_tags");
            $("#possible_tags").append(document.createTextNode(" "));
          });
    current_app = $('input[name="app_label"]').val();
    current_object_type = $('input[name="object_type"]').val();
    current_id = $('input[name="id"]').val();
    // currently committeemeeting urls have a unique structure. clean this up.
    if (current_id == 'meeting') {
        current_object_type = 'committeemeeting';
        current_id = window.location.pathname.split('/')[3];
    }
    var url = '/api/tag/'+current_app+'/'+current_object_type+'/'+current_id+'/';
    $.ajax({url: url, success: mark_selected_tags, cache: false});
    $('#create_tag').show();
    $('#create_tag_form').submit(function(){
        var csrf = $('input[name="csrfmiddlewaretoken"]').val();
        var tag = $('#tag').val();
        $.post("/tags/"+current_app+"/"+current_object_type+"/"+current_id+"/create-tag/",
            { tag: tag, csrfmiddlewaretoken: csrf }, add_tag_callback );
        return false;
    });
}

function mark_selected_tags(data){
    $.each(data, function(i,item){
        $("#possible_tag_"+item.id).addClass("selected");
        selected_tags[item.id]=1;
    });
}

function toggle_tag(tag_id) {
    var csrf = $('input[name="csrfmiddlewaretoken"]').val();
    if (tag_id in selected_tags){
        $.post("/tags/"+current_app+"/"+current_object_type+"/"+current_id+"/remove-tag/",
                { tag_id: tag_id, csrfmiddlewaretoken: csrf }, remove_tag_callback );
        $("#possible_tag_"+tag_id).removeClass("selected");
        delete selected_tags[tag_id];
    } else {
        $.post("/tags/"+current_app+"/"+current_object_type+"/"+current_id+"/add-tag/",
                { tag_id: tag_id, csrfmiddlewaretoken: csrf }, add_tag_callback );
        $("#possible_tag_"+tag_id).addClass("selected");
        selected_tags[tag_id] = 1;
    }
}

function add_tag_callback(data) {
    var item = eval('('+data+')');
    $('#no-tags-yet').remove();
    if( $("#tag_"+item.id).length == 0 ){ // we don't already have this tag.
        var href = item.url;
        $('<a class="tag">').attr("id", "tag_"+item.id).attr("href", href).html(item.name).appendTo("#tags");
        $("#tags").append(document.createTextNode(" "));
    };
    if( $("#possible_tag_"+item.id).length == 0 ){ // we don't already have this tag in the possible list.
        href = "javascript:toggle_tag("+item.id+");";
        $('<a class="tag">').attr("id", "possible_tag_"+item.id).attr("href", href).html(item.name).appendTo("#possible_tags");
        $("#possible_tags").append(document.createTextNode(" "));
    };
    $("#possible_tag_"+item.id).addClass("selected");
    selected_tags[item.id]=1;
}

function remove_tag_callback(data) {
    var item = eval('('+data+')');
    $('#tag_'+item.id).remove();
}
