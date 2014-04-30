
lobbyists = {
    _ui_disabled: false,
    mark_alias_corporation: function(alias_corporation_id) {
        if (this._ui_disabled) return;
        this._ui_disabled = true;
        alert('click on the "real" corporation');
        $('.lobbyist-corporation').each(function(){
            if ($(this).data('corporation-id') == alias_corporation_id) {
                $(this).css('background-color', 'grey');
            } else {
                var main_corporation_id = $(this).data('corporation-id');
                $(this).find('.lobbyist-corporation-edit-box')
                    .hide()
                    .after('<p class="lobbyist-corporation-temp-edit-box"><a href="javascript:lobbyists.mark_real_corporation('+alias_corporation_id+','+main_corporation_id+')">This is the real corporation</a></p>');
            }
        });
    },
    mark_real_corporation: function(alias_corporation_id, main_corporation_id) {
        var url = '/lobbyist/corporation/mark_alias/'+alias_corporation_id+'/'+main_corporation_id;
        $.get(url, function(res) {
            if (!res.ok) {
                alert("Error marking corporation alias: "+res.msg);
            } else {
                alert("OK");
            }
            $('.lobbyist-corporation-temp-edit-box').remove();
            $(".lobbyist-corporation[data-corporation-id='"+alias_corporation_id+"']").css('background-color', '');
            $('.lobbyist-corporation-edit-box').show();
            lobbyists._ui_disabled = false;
        });
    }
};
