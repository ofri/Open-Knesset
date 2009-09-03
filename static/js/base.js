var API_URL = '/api/';
var Cycle = -1;
var Moving = true; // system is in transition, most things don't work
var Buttons = $('#nav_global li');
var CurrentState = null;


function BreadCrumb() {
    this.params= {num:20, page:0};
    this.expanded = {}; // an object that holds IDs of expanded items.
    return this;
}

BreadCrumb.prototype.isList = function () {
    // is this is about a list?
    return !this.hasOwnProperty('pk') ;
};

BreadCrumb.prototype.refresh = function() {
    $(this.nav_id).addClass('selected');
    if (this.isList()) { this.pullList(this.cls); }
    else               { this.pullObject(this.cls); }
};

BreadCrumb.prototype.more = function() {
    this.params.page ++;
    this.pullList(); //callback function when rendering is done
};

BreadCrumb.prototype.getFeedUrl = function(i){
    var r = API_URL + this.name + '/';
    if (typeof i == "number") { r +=  i + '/'; }
    return r;
};

BreadCrumb.prototype.pullList = function(cb) {
    var i = this;
    $.getJSON(this.getFeedUrl(),
        this.params, // just added params - need other mthod get JSON fails
        function(data){
            i.endMove();
            if (typeof cb == 'function') { cb(i); }
            $('#items-list').append(i.renderList(data));
        });
};

BreadCrumb.prototype.pullObject = function(cb) {
    $.getJSON(this.getFeedUrl()+this.pk+'/',
        function(data){
            cb(data);
            $('#items').html(data);
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
        $.getJSON(this.getFeedUrl(i),
                    function(data){
                        html = $('#'+i).html();
                        $('#'+i).addClass("expanded").append(CurrentState.renderItem(data));
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
    ret = "";
    ret = '<div class="item_div">'+CurrentState.div_view(data)+'</div>';
    return ret;
};

BreadCrumb.prototype.startMove = function () {
    Moving = true;
    $("#items").html('Loading...');
    if (CurrentState !== null) { $(CurrentState.nav_id).removeClass('selected'); };
    Buttons.addClass('Limbo');
};

BreadCrumb.prototype.endMove = function () {
    $('#nav-' + CurrentState.name).addClass('current');
    Buttons.removeClass('Limbo');
    Moving = false;
};

BreadCrumb.prototype.cls = function (i) {
    // clear the screen
    if (i.isList())
        $("#items").html('<ul id="items-list"></ul>'); // TODO: there has to be a simpler way
    else
        $("#items").html('');
};

function go (hashpath) {
    // jumps to a specific state and if pk is specified, a specific object 
    // var _parse_hashpath = /^([A-Za-z]+)\/(?:(\d+)\/)?$/;
    CurrentState != null && CurrentState.startMove();
    var _parse_hashpath = /^([A-Za-z]+)\/(\d*)/;
    var state_name, pk;
    vars = _parse_hashpath.exec(hashpath) ;
    if (vars[1] != "") {
        state_name = vars[1];
        pk = vars[2] != ""?vars[2]:0;
    }
    else {
        state_name = DEFAULT_STATE;
        pk = 0;
    }
    // TODO: del CurrentState;
    CurrentState = States[state_name](pk);
    CurrentState.refresh();
};

function renderContent(html){
    $('#content-main').html(html);
}   

