var API_URL = '/api/'
var Cycle = -1;
var History = new Array(); // remeber history 
var Moving = false; // system is in transition, most things don't work
var Buttons = $('#nav_global li');

// from the good parts
Object.create = function (o) {
    var F = function () {} ;
    F.prototype=o;
    return new F();
};

var BreadCrumb = function (name) {
    this.name = name;
};
BreadCrumb.prototype.refresh = function() {
    $('#nav-' + this.name).addClass('current');
    $('#nav-back').toggleClass('disabled', Cycle==0);
    $('#nav-forward').toggleClass('disabled', Cycle==History.length-1);
    this.pullList(function () { //callback function when rendering is done
        if (Moving) {
            Buttons.removeClass('Limbo');
            Moving = false;
        }
    });
}
BreadCrumb.prototype.params = {num:20,page:0};
BreadCrumb.prototype.getFeedUrl = function (i){
    var r = API_URL + this.name + '/';
    if (typeof i == "number") { r +=  i + '/'; }
    return r;
};
BreadCrumb.prototype.pullList = function (cb) {
    $.getJSON(this.getFeedUrl(),
            function(data){
              $.each(data.items, function(i,item){
                this.listElement(item).appendTo("#list-items");
              });
              cb(data);
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
              $.each(data.items, function(i,item){
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
    Buttons.addClass('Limbo');
}
function goBack(){
    if (!Moving && Cycle > 0) {
        History[Cycle] = CurrentState; // remember current state
        startMove();
        Cycle--;
        CurrentState=History[Cycle];
        refresh();
    }
}

function goForward(){
    if (!Moving && Cycle < History.length-1) {
        startMove();
        Cycle++;
        CurrentState=History[Cycle];
        refresh();
   }
}
function renderContent(html){
    $('#content-main').html(html);
}   
// now, the stateis definitions
var CurrentState = new BreadCrumb ({
    name: 'stream',
    listElment: function (item) {
        var html = item.title + " +" + item.ForVotesCount+ " -" + item.AgainstVoteCount
        return $("A").attr("href", this.getFeedUrl(item.id)).html(html);
        }
});
CurrentState.refresh();
