function get_tags_list() {
    $("#possible_tags").html('');
    $.getJSON('/api/tag/', get_tags_list_callback );

}

function get_tags_list_callback(data) {
    $.each(data, function(i,item){
            var href = "javascript:suggest_tag("+item.id+");";            
            $('<a class="awesome-button small dontwrap">').attr("id", "tag_"+item.id).attr("href", href).html(item.name).appendTo("#possible_tags");
            $("#possible_tags").append(document.createTextNode(" "));
          });
    $.getJSON('/api/tag/'+window.location.pathname.split('/')[1]+
        '/'+window.location.pathname.split('/')[2]+'/', mark_selected_tags);
}

function mark_selected_tags(data){
    $.each(data, function(i,item){
        $("#tag_"+item.id).addClass("selected");    
    });

}

function suggest_tag(tag_id) {
    $.post("suggest-tag/", { tag_id: tag_id }, suggest_tag_callback );
    $("#tag_"+tag_id).addClass("selected");
}

function suggest_tag_callback(data) {
    
}
