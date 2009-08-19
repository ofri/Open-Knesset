var API_URL = '/api/'
var Cycle = -1;
var History = new Array(); // remeber history 
var Moving = true; // system is in transition, most things don't work
var Buttons = $('#nav_global li');
var CurrentState = null;

// from the good parts
Object.create = function (o) {
    var F = function () {} ;
    F.prototype=o;
    return new F();
};

var BreadCrumb = function (name, renderList) {
    this.name = name;
    this.renderList = renderList;
};
BreadCrumb.prototype.refresh = function() {
    $('#nav-' + this.name).addClass('current');
    $('#nav-back').toggleClass('disabled', Cycle==0);
    $('#nav-forward').toggleClass('disabled', Cycle==History.length-1);
    this.pullList(endMove); //callback function when rendering is done
}
BreadCrumb.prototype.params = {num:20,page:0};
BreadCrumb.prototype.getFeedUrl = function (i){
    var r = API_URL + this.name + '/';
    if (typeof i == "number") { r +=  i + '/'; }
    return r;
};
BreadCrumb.prototype.pullList = function (cb) {
    $.getJSON(this.getFeedUrl(),
            this.params, // just added params - need other mthod get JSON fails
            function(data){
                $('#items-list').append(CurrentState.renderList(data));
                // cb(data);
            });
};
BreadCrumb.prototype.pullItem = function (i) {
    $.getJSON(this.getFeedUrl(i),
            function(data){
              $.each(data.items, function(i,item){
                this.itemElement().appendTo("#item");
              })
            });
};

BreadCrumb.prototype.nextPage = function () {
    this.params.page++;
    $.getJSON(API_URL+this.name+'/', this.params, 
            function(data){
              jQuery.each(data.items, function(i,item){
                $("<li>").html(this.render()).appendTo("#items");
              });
            });
};

function jsr(to) {
    startMove();
    if (Cycle >= 0){
        History[Cycle] = CurrentState;
    }
    Cycle++;
    CurrentState = new BreadCrumb(to);
    var ancientHistory = History.length-Cycle;
    if (ancientHistory>0){
        History.splice(Cycle, ancientHistory);
    }
    CurrentState.refresh();
}
function startMove() {
    Moving = true;
    $('#nav-' + CurrentState.name).delClass('current');
    Buttons.addClass('Limbo');
}
function endMove() {
    Moving = False;;
    $('#nav-' + CurrentState.name).addClass('current');
    Buttons.delClass('Limbo');
}
function goBack(){
    if (!Moving && Cycle > 0) {
        History[Cycle] = CurrentState; // remember current state
        startMove();
        Cycle--;
        CurrentState=History[Cycle];
        CurrentState.refresh();
    }
}

function goForward(){
    if (!Moving && Cycle < History.length-1) {
        startMove();
        Cycle++;
        CurrentState=History[Cycle];
        CurrentState.refresh();
   }
}
function renderContent(html){
    $('#content-main').html(html);
}   
// now, init code
$(document).ready (function () {
    CurrentState = new BreadCrumb (name='member', 
        renderList=function (data) {
            ret = "";
            $.each(data, function(i,item){
                var li =$("#items-list li:first").clone(true);
                var a = $("#items-list li:first a").clone(true);
                var one_liner = item.name + " " + item.start_date + " - " + item.end_date;
                var href = "javascript:CurrentState.renderItem("+ item.id + ");";
                ret += '<li><a href='+ href +'>'+ one_liner +'</a></li>';
            });
            return ret;
        });
    CurrentState.refresh();
});
