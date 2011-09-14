function register_watch(object_id, object_type, watch_text, unwatch_text, watched_object, follow_url) {
     if (watched_object) {
        document.is_watched = true;
        $('#watch').html(unwatch_text);
     } else {
        document.is_watched = false;
        $('#watch').html(watch_text);
     }
    $('#watch').click( function () {
        if (document.is_watched) {
            jQuery.ajax({
                type: 'POST',
                url: follow_url,
                data: {'verb': 'unfollow',
                       'id': object_id,
                       'what': object_type},
                context: $('#watch'),
                success: function () {
                    document.is_watched = false;
                    this.html(watch_text);
                },
                error:  function(request, textStatus, error) {
                    var msg = $("#message_unknown").html()
                    $.jGrowl(msg, {life: 5000});
                    $('#message_login').show();
                }
            });
        }
        else {
            jQuery.ajax({
                type: 'POST',
                url: follow_url,
                data: {'verb': 'follow',
                       'id': object_id,
                       'what': object_type},
                context: $('#watch'),
                success: function () {
                    document.is_watched = true;
                    this.html(unwatch_text);
                },
                error:  function(request, textStatus, error) {
                    var msg = $("#message_login").html()
                    $.jGrowl(msg, {sticky: true});
                }
            });
        }
        return (false);
    })
}
