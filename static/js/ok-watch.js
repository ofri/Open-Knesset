!function ($) {

  "use strict"; // jshint ;_;

  $(function() {

    var $watcher = $('#watcher'),
        $watch = $('#watch'),
        $login = $('#watch-login'),
        $error = $('#watch-error'),
        $num = $('#watch-followers'),
        wdata = $watcher.data(),
        can_watch = false,
        watched = false,
        followers = 0; 

    // First we check whether the user can watch at all
    $.get(wdata.isFollowingUrl, {'id': wdata.watchId, 'what': wdata.watchType})
    .done(function(data){
        can_watch = data.can_watch;
        followers = data.followers;
        watched = data.watched;

        if (can_watch) {
            $watch.text(watched ? wdata.unwatchText : wdata.watchText);
        }

        $num.show();
        $num.text(followers);
    })
    .fail(function(response) {
        $watch.hide();
        $login.hide();
        $error.text(response.responseText).show();
        $num.parent().hide();
        $watcher.show();
    });

    // Bind the button
    $watch.click(function(e){
        e.preventDefault();

		if (!can_watch) {
			$login.show();
			return false;
		}
        $watch.button('loading');
        $.post(wdata.watchUrl, {verb: watched ? 'unfollow' : 'follow', id: wdata.watchId,  'what': wdata.watchType})
        .done(function(data) {
            $watch.button('reset')
            watched = data.watched;
            $watch.text(watched ? wdata.unwatchText : wdata.watchText);
            followers = data.followers;
            $num.text(followers);
        })
        .fail(function() {$watch.button('reset')});
    });

  }) // end ready
}(window.jQuery);
