var selected_tags = {};
var current_id = "";
var current_object_type = "";
var current_app = "";

function get_tags_list(url) {
    if (typeof(url) === 'undefined') {
        url = '/api/v2/tag/?format=json&limit=100'
    }
    $.ajax({url: url, success: get_tags_list_callback, cache: false});
}

function add_nav_button(text, url) {
    if (url !== null) {
        $('<a class="btn btn-small">').attr('href', "javascript:get_tags_list('"+encodeURIComponent(url)+"')").html(text).appendTo("#possible_tags");
    }
}

function get_tags_list_callback(data) {
    $("#possible_tags").html('<br/>');
    $.each(data['objects'], function(i,item){
            var href = "javascript:toggle_tag("+item.id+");";
            $('<a class="tag">').attr("id", "possible_tag_"+item.id).attr("href", href).html(item.name).appendTo("#possible_tags");
            $("#possible_tags").append(document.createTextNode(" "));
          });
    meta = data['meta'];

	if (meta) { 
		$("#possible_tags").append('<br/>');
		add_nav_button(gettext('previous'), meta['previous']);
		add_nav_button(gettext('next'), meta['next']);
	}
    current_app = $('#add_tags').data('appLabel');
    current_object_type = $('#add_tags').data('objectType');
    current_id = $('#add_tags').data('id');
    // currently committeemeeting urls have a unique structure. clean this up.
    if (current_id == 'meeting') {
        current_object_type = 'committeemeeting';
        current_id = window.location.pathname.split('/')[3];
    }
    var url = '/api/v2/tag/'+current_app+'/'+current_object_type+'/'+current_id+'/';
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
    $.each(data['objects'], function(i,item){
        $("#possible_tag_"+item.id).addClass("selected label");
        selected_tags[item.id]=1;
    });
}

function toggle_tag(tag_id) {
    var csrf = $('input[name="csrfmiddlewaretoken"]').val();
    if (tag_id in selected_tags){
        $.post("/tags/"+current_app+"/"+current_object_type+"/"+current_id+"/remove-tag/",
                { tag_id: tag_id, csrfmiddlewaretoken: csrf }, remove_tag_callback );
        $("#possible_tag_"+tag_id).removeClass("selected label");
        delete selected_tags[tag_id];
    } else {
        $.post("/tags/"+current_app+"/"+current_object_type+"/"+current_id+"/add-tag/",
                { tag_id: tag_id, csrfmiddlewaretoken: csrf }, add_tag_callback );
        $("#possible_tag_"+tag_id).addClass("selected label");
        selected_tags[tag_id] = 1;
    }
}

function add_tag_callback(data) {
    var item = eval('('+data+')');
    $('#no-tags-yet').remove();
    if( $("#tag_"+item.id).length == 0 ){ // we don't already have this tag.
        var href = item.url;
        $('<a class="tag label">').attr("id", "tag_"+item.id).attr("href", href).html(item.name).appendTo("#tags");
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

/*** new tags ***/
/*** currently only for committeemeeting ***/

window.tags={
    init:function(data){
        this._model.init(
            data['csrf'],
            data['app_label'],
            data['object_type'],
            data['object_id']
        );
    },
    edit:function(){
        this._view.edit();
    },
    doneEdit:function(){
        this._view.doneEdit();
    },
    add:function(){
        var _this=this;
        var name=_this._view.getAddTagName();
        if (name.length>0 && _this._view.lock()) {
            /*
                there are bugs with trying to add tag id directly
                disabled for now, need to investigate further
            */
            var id=false;//_this._view.getAddTagId();
            if (id===false) {
                _this._model.addByName(name,function(tmp,id){
                    if (tmp===true) {
                        _this._view.add(name,id);
                        _this._view.clearAddTagName();
                    } else {
                        _this._view.error(tmp);
                    };
                    _this._view.unlock();
                },function(id){
                    return _this._view.isTagIdExists(id);
                });
            } else if (_this._view.isTagIdExists(id)) {
                _this._view.error(gettext('tag is already attached to current object'));
                _this._view.unlock();
            } else {
                _this._model.add(id,function(tmp){
                    if (tmp===true) {
                        _this._view.add(name,id);
                    } else {
                        _this._view.error(tmp);
                    };
                    _this._view.unlock();
                });
            };
        };
    },
    del:function(id){
        var _this=this;
        if (_this._view.lock()) {
            _this._model.del(id,function(tmp){
                if (tmp===true) {
                    _this._view.del(id);
                } else {
                    _this._view.error(tmp);
                };
                _this._view.unlock();
            });
        };
    },
    unDel:function(id){
        var _this=this;
        if (_this._view.lock()) {
            _this._model.add(id,function(tmp){
                if (tmp===true) {
                    _this._view.unDel(id);
                } else {
                    _this._view.error(tmp);
                };
                _this._view.unlock();
            });
        };
    },
    _model:{
        _getTagId:function(name,callback){
            $.get(
                '/api/v2/tag/',
                {'format':'json','name':name},
                function(data){
                    if (data.objects.length!=1) {
                        callback(gettext('the specified tag name does not exist and you do not have permission to add new tag names, only to attach existing tags'));
                    } else {
                        callback(true,data.objects[0].id);
                    };
                }
            );
        },
        init:function(csrf,app_label,object_type,object_id){
            this._csrf=csrf;
            this._app_label=app_label;
            this._object_type=object_type;
            this._object_id=object_id;
        },
        del:function(id,callback){
            $.post(
                "/tags/"+this._app_label+"/"+this._object_type+"/"+this._object_id+"/remove-tag/",
                {tag_id:id,csrfmiddlewaretoken:this._csrf},
                function(data){callback(true);}
            );
        },
        add:function(id,callback){
            $.post(
                "/tags/"+this._app_label+"/"+this._object_type+"/"+this._object_id+"/add-tag/",
                {tag_id:id,csrfmiddlewaretoken:this._csrf},
                function(data){callback(true);}
            );
            
        },
        addByName:function(name,callback,isTagIdExists){
            var self=this;
            this._getTagId(name,function(tmp,id){
                if (tmp===true) {
                    if (isTagIdExists(id)) {
                        callback(gettext('tag is already attached to current object'));
                    } else {
                        self.add(id,function(tmp){
                            callback(tmp,id);
                        });
                    };
                } else {
                    callback(tmp);
                };
            });
        }
    },
    _view:{
        _onDelButtonClick:function(elt){
            if ($(elt).data('isDeleted')=='yes') {
                tags.unDel($(elt).data('tagid'));
            } else {
                tags.del($(elt).data('tagid'));
            };
        },
        isTagIdExists:function(id){
            return ($('#tag_'+id).length>0);
        },
        lock:function(){
            $("body").css("cursor", "wait");
            $('.tagdelbutton').css('cursor','wait');
            $('.tag').css('cursor','wait');
            $('#tags_addnew a').css('cursor','wait');
            $('#tags_addnew input').css('cursor','wait');
            if (tags._viewLocked) {
                return false;
            } else {
                tags._viewLocked=true;
                return true;
            };               
        },
        unlock:function(){
            tags._viewLocked=false;
            $("body").css("cursor", "default");
            $('.tagdelbutton').css('cursor','pointer');
            $('.tag').css('cursor','pointer');
            $('#tags_addnew a').css('cursor','pointer');
            $('#tags_addnew input').css('cursor','auto');
        },
        getAddTagName:function(){
            return $('#tags_addnew input').val();
        },
        getAddTagId:function(){
            var data=this._autocomplete.data;
            if (data.length==1) {
                return data[0];
            } else {
                return false;
            };
        },
        clearAddTagName:function(){
            $('#tags_addnew input').val('');
        },
        add:function(name,id,href){
            var html='';
            html+='<a id="tag_'+id+'" class="tag label" style="cursor: pointer;"></a>';
            html+='<span style="cursor: pointer; color: red;" class="tagdelbutton" data-tagid="'+id+'" id="deltag_'+id+'">&nbsp;'+gettext('Delete')+'&nbsp;<br></span>';
            $('#tags').append(html);
            $('#tag_'+id).attr('href','/tags/'+name+'/');
            $('#tag_'+id).text(name);
            var _this=this;
            $('#deltag_'+id).click(function(){
                _this._onDelButtonClick(this);
            });
        },
        edit:function(){
            var _this=this;
            if ($('.tagdelbutton').show().length==0) {
                $('.tag').each(function(){
                    var tagid=$(this).attr('id').split('_')[1]
                    $(this).after('<span style="cursor:pointer;color:red;" class="tagdelbutton" data-tagid="'+tagid+'" id="deltag_'+tagid+'">&nbsp;'+gettext('Delete')+'&#160;<br/></span>');
                });
                $('.tagdelbutton').click(function(){
                    _this._onDelButtonClick(this);
                });
                _this._autocomplete=$('#tags_addnew input').autocomplete({
                    delimiter: ', ',
                    serviceUrl: '/api/v2/tag/',
                    params: {limit:50,jquery_autocomplete:1},
                    paramName: 'name__startswith',
                });
                $('#no-tags-yet').hide();
            };
            $('#tags_edit').hide();
            $('#tags_doneedit').show();
            $('#tags_addnew').show();
        },
        doneEdit:function(){
            $('.tagdelbutton').hide();
            $('#tags_edit').show();
            $('#tags_doneedit').hide();
            $('#tags_addnew').hide();
            $('.tag').css({
                'text-decoration':'',
                'background-color':'',
                'color':''
            });
            $('.tagdelbutton').hide();
            $('.tagdelbutton').each(function(){
                if ($(this).data('isDeleted')=='yes') {
                    $(this).prev().remove();
                    $(this).remove();
                };
            });
        },
        unDel:function(id){
            $('#tag_'+id).css({
                'text-decoration':'',
                'background-color':'',
                'color':''
            });
            $('#deltag_'+id).html(gettext('Delete')+'<br/>');
            $('#deltag_'+id).data('isDeleted','no');
        },
        del:function(id){
            $('#tag_'+id).css({
                'text-decoration':'line-through',
                'background-color':'#dddddd',
                'color':'#aaaaaa'
            });
            $('#deltag_'+id).html(gettext('Undo Delete')+'<br/>');
            $('#deltag_'+id).data('isDeleted','yes');
        },
        error:function(msg){
            alert(msg);
        }
    }
};


