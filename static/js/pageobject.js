var current_page = null;

function PageObject(params) {
    this.params = params;
    this.params.part = true;
    if (!this.params.cls) this.params.cls = "";
    if (!this.params.content_at) this.params.content_at = this.params.page_at;
    this.moving = false;
    return this;
}

PageObject.prototype.clone = function() {
    that = new PageObject(this.params);
    return that;
}

PageObject.prototype.refresh = function() {
    if (!this.params.more_at) { this.pullObject(true); }
    else                   { this.pullList(true); }
};

PageObject.prototype.more = function() {
    current_page.params.page ++;
    current_page.pullList(); //callback function when rendering is done
    return false;
};

PageObject.prototype.updateList = function(data,cls) {
    if (cls) { 
        $(this.params.page_at).html(this.params.cls) 
    };
	$(this.params.content_at).append(data);
    $(this.params.more_at).click(this.more);
};

PageObject.prototype.pullList = function(cls) {
    $.ajax({ type: "GET", 
        url: this.params.url,
        data: {part: 1, page: this.params.page}, 
        success: function(data){
	    	current_page.updateList(data,cls);
            current_page.endMove();
        },
        error: function(response, textStatus, errorThrown) {
            if (response.status==404) {
                $(current_page.params.more_at).html(gettext('no more'));
                //TODO: remove the click event
                }
            else alert ("strange error GETing a list");
        },
        dataType:'html'});
};

PageObject.prototype.updateObject = function(data,cls) {
    if (typeof cls != 'undefined') { $(this.params.page_at).html(this.params.cls) };
	$(this.params.content_at).append(data);
};

PageObject.prototype.pullObject = function(cls) {
    $.get(this.params.url,
        {part: 1}, 
        function(data){
	    	current_page.updateObject(data,cls);
            current_page.endMove();
        });
};

PageObject.prototype.startMove = function () {
    this.moving = true;
    // TODO: need to get rid of this constant
    //  $(this.params.header_at).html(gettext('Loading...'));
    $(this.params.header_at).html("<img src='/static/img/ajax-loader.gif'>");
    if (current_page !== null) { $(current_page.params.nav_id).removeClass('selected'); };
};

// update all links to use hash navigation
function hashHrefs(q) {
    $(q).each(function (){
        var href = $(this).attr('href');
        if(typeof href != "undefined" && href[0]=='/' && href[1]!='#'){
            href = '/#'+href.substr(1);
            $(this).attr('href',href);
        };
    });    
}
PageObject.prototype.endMove = function () {
    $(this.params.nav_id).addClass('selected');
    if (this.params.hasOwnProperty("header_at")) $(this.params.header_at).html(this.params.header);
    else $("#content-main h1").html(this.params.header);

    hashHrefs(this.params.page_at+' a.hashnav');
    this.moving = false;
};

    /*
			if (this.hasMore) {
				a += '<a id="more" href="javascript:CurrentState.more();">'+
				gettext("more") +
				'</a>'; // TODO: there has to be a simpler way
			}
    }
    */

function go (path, params) {
    var _parse_path = /([A-Za-z\-]+)\/((\d*)\/)?$/;
    var page_name, id;

    if (current_page != null) { current_page.startMove() };

    var p=(path=="")?document.location.pathname:path;
    var vars = _parse_path.exec(p) ;
    if (vars !== null && vars[1] != "") {
        current_page = Pages[vars[1]].clone();
        current_page.params.url = p;
        current_page.params.page = 1;
        if (vars[2]) current_page.params.id = parseInt(vars[2]);
        for (attrname in params) { current_page.params[attrname] = params[attrname]; };
        if (path!="") current_page.refresh();
    }
    else {
        current_page = Pages['main'].clone();
        current_page.params.url = '/';
        for (attrname in params) { current_page.params[attrname] = params[attrname]; };
        current_page.refresh();
        }
};
