var API_URL = '/api/';
var Cycle = -1;
var Moving = true; // system is in transition, most things don't work
var CurrentState = null;
var HEADER = "#content-main h1";
var CONTENT = "#content-main div";

function BreadCrumb() {
    this.params= {num:20, page:0};
    this.expanded = {}; // an object that holds IDs of expanded items.
    return this;
}

BreadCrumb.prototype.isList = function () {
    // is this is about a list?
    return !this.hasOwnProperty('id') ;
};

BreadCrumb.prototype.refresh = function() {
    if (this.isList()) { this.pullList(cls=true); }
    else               { this.pullObject(true); }
};

BreadCrumb.prototype.hasMore = true;
BreadCrumb.prototype.more = function() {
    this.params.page ++;
    this.pullList(); //callback function when rendering is done
};

BreadCrumb.prototype.getFeedUrl = function(i){
    var r = API_URL + this.name + '/';
    if (typeof i == "number") { r +=  i + '/'; }
    r += 'htmldiv/';
    return r;
};

BreadCrumb.prototype.updateList = function(data,cls) {
    if (typeof cls != 'undefined') { $(CONTENT).html(CurrentState.cls()) };
	$(CONTENT).append(data);
};

BreadCrumb.prototype.pullList = function(cls) {
    $.get(this.getFeedUrl(),
        this.params, // just added params - need other mthod get JSON fails
        function(data){
	    	CurrentState.updateList(data,cls);
            CurrentState.endMove();
        },
	'html');
};

BreadCrumb.prototype.updateObject = function(data,cls) {
    if (typeof cls != 'undefined') { $(CONTENT).html(CurrentState.cls()) };
	$(CONTENT).append(data);
};

BreadCrumb.prototype.pullObject = function(cls) {
    $.get(this.getFeedUrl(this.id),
	this.params,
        function(data){
	    	CurrentState.updateObject(data,cls);
            CurrentState.endMove();
        });
};

BreadCrumb.prototype.toggleItem = function(i){
    if (i in this.expanded) { // this item is already expanded
        delete this.expanded[i];
        $('#'+i+' > div').fadeOut();
    } else { // not expanded yet:
        this.expanded[i] = ''; // add this to the expanded object.
        this.pullItem(i);
    }
};
BreadCrumb.prototype.pullItem = function(i) {
        //TODO: add item cache. if item is in cache, don't call API. just show it.        
        $.get(this.getFeedUrl(i),
		this.params,
	    	function(data){
                        $('#'+i).addClass("expanded").append(data);
                      //$.each(data.items, function(i,item){
                      //  this.itemElement().appendTo("#item");
                      //})
                    }
                );
};

BreadCrumb.prototype.renderList = function (data) {
    ret = "";
    $.each(data, function(i,item){
        var href = "javascript:CurrentState.toggleItem("+ item.id + ");";
        ret += '<li id='+ item.id +'><a href='+ href +'>'+ CurrentState.one_liner(item) +'</a></li>';
    });
    return ret;
};

BreadCrumb.prototype.renderItem = function (data) {
    return data;
};

BreadCrumb.prototype.startMove = function () {
    Moving = true;
    $(HEADER).html(gettext('Loading...'));
    if (CurrentState !== null) { $(CurrentState.nav_id).removeClass('selected'); };
    $('#more').die();
};

updateLinks = function () {
    $("a").each(function (){
        var href = $(this).attr('href');
        if(typeof href != "undefined" && href[0]=='/' && href[1]!='#'){
            href = '/#'+href.substr(1);
            $(this).attr('href',href);
        };
    });    
};

BreadCrumb.prototype.endMove = function () {
    $(this.nav_id).addClass('selected');
    $('#content-main h1').html(CurrentState.header);
    updateLinks();
    Moving = false;
};

BreadCrumb.prototype.cls = function () {
    // clear the screen and prepare it for CurrentState
    var i = CurrentState;
    var a = '';
    if (i.isList()) {
			if (i.hasMore) {
				a += '<a id="more" href="javascript:CurrentState.more();">'+
				gettext("more") +
				'</a>'; // TODO: there has to be a simpler way
			}
    }
	return a;
};

function go (hashpath, params) {
    // jumps to a specific state and if id is specified, a specific object 
    if (hashpath=="") { return; };
    var _parse_hashpath = /^([A-Za-z\-]+)\/(\d*)/;
    var state_name, id;

    if (CurrentState != null) { CurrentState.startMove() };

    vars = _parse_hashpath.exec(hashpath) ;
    if (vars !== null && vars[1] != "") {
        state_name = vars[1];
        id = vars[2] != ""?parseInt(vars[2]):undefined;
    }
    else {
        state_name = DEFAULT_STATE;
        id = undefined;
    }
    CurrentState = States[state_name](id);
    for (attrname in params) { CurrentState.params[attrname] = params[attrname]; };
    CurrentState.refresh();
};

function renderContent(html){
    $('#content-main').html(html);
}   

