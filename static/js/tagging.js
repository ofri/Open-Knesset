var selected_tags = {};

function get_tags_list() {
    $("#possible_tags").html('');
    $.getJSON('/api/tag/', get_tags_list_callback );

}

function get_tags_list_callback(data) {
    $.each(data, function(i,item){
            var href = "javascript:toggle_tag("+item.id+");";
            $('<a class="tag">').attr("id", "possible_tag_"+item.id).attr("href", href).html(item.name).appendTo("#possible_tags");
            $("#possible_tags").append(document.createTextNode(" "));
          });
    var url = '/api/tag/'+window.location.pathname.split('/')[1]+'/'+window.location.pathname.split('/')[2]+'/';
    $.ajax({url: url, success: mark_selected_tags, cache: false});
}

function mark_selected_tags(data){    
    $.each(data, function(i,item){
        $("#possible_tag_"+item.id).addClass("selected");
        selected_tags[item.id]=1;
    });
}

function toggle_tag(tag_id) {
    if (tag_id in selected_tags){
        $.post("remove-tag/", { tag_id: tag_id }, remove_tag_callback );
        $("#possible_tag_"+tag_id).removeClass("selected");
        delete selected_tags[tag_id];
    } else {
        $.post("add-tag/", { tag_id: tag_id }, add_tag_callback );
        $("#possible_tag_"+tag_id).addClass("selected");
        selected_tags[tag_id] = 1;
    }
}

function add_tag_callback(data) {    
    var item = eval('('+data+')');
    $('#no-tags-yet').remove();
    var href = "javascript:toggle_tag("+item.id+");";
    $('<a class="tag">').attr("id", "tag_"+item.id).attr("href", href).html(item.name).appendTo("#tags");
    $("#tags").append(document.createTextNode(" "));
}

function remove_tag_callback(data) {
    var item = eval('('+data+')');
    $('#tag_'+item.id).remove();
}
