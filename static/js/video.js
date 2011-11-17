$(function(){
    $('.video_playbtn').click(function(){
        var parent=$(this).parent();
        var embed_link=parent.attr('embed_link').replace('https://','http://');
        var player='<div>'
            +'<iframe src="'+embed_link+'" width="'+$(this).width()+'" height="'+$(this).height()+'" frameborder="0">'
        +'</div>';
        parent.before(player);
        parent.hide();
    });
});
