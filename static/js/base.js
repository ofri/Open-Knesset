var API_URL = '/api/'
var Cycle = -1;
var History = new Array(); // remeber history 
var Moving = true; // system is in transition, most things don't work
var Buttons = $('#nav_global li');
var CurrentState = null;


function BreadCrumb () {
    this.params= {num:20, page:0};
    this.expanded = {}; // an object that holds IDs of expanded items.
    // from the good parts
    this.refresh = function() {
        $(this.nav_id).addClass('selected');
        $('#nav-back a').toggleClass('disabled', Cycle==0);
        $('#nav-forward a').toggleClass('disabled', Cycle==History.length);
        this.pullList(endMove); //callback function when rendering is done
    };
    this.more = function() {
        this.params.page ++;
        this.pullList(endMove); //callback function when rendering is done
    };
    this.getFeedUrl = function(i){
        var r = API_URL + this.name + '/';
        if (typeof i == "number") { r +=  i + '/'; }
        return r;
    };
    this.pullList = function(cb) {
        $.getJSON(this.getFeedUrl(),
            this.params, // just added params - need other mthod get JSON fails
            function(data){
                $('#items-list').append(CurrentState.renderList(data));
                cb(data);
            });
    };

    this.toggleItem = function(i){
        if (i in this.expanded) { // this item is already expanded
            // currently, do nothing.
            // TODO: close it.
            delete this.expanded[i];
            $('#'+i+' > div').fadeOut();
        } else { // not expanded yet:
            this.expanded[i] = ''; // add this to the expanded object.
            this.pullItem(i);
        }
    }
    this.pullItem = function(i) {
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
    }
    this.renderList = function (data) {
            ret = "";
            $.each(data, function(i,item){
                var href = "javascript:CurrentState.toggleItem("+ item.id + ");";
                ret += '<li id='+ item.id +'><a href='+ href +'>'+ CurrentState.one_liner(item) +'</a></li>';
            });
            return ret;
        };
    this.renderItem = function (data) {
        ret = "";
        ret = '<div class="item_div">'+CurrentState.div_view(data)+'</div>';
        return ret;
        
    }
    return this;
};
function jsr(to) {
    startMove();
    if (Cycle >= 0){
        History[Cycle] = CurrentState;
    }
    Cycle++;
    CurrentState = to();
    var ancientHistory = History.length-Cycle;
    if (ancientHistory>0){
        History.splice(Cycle, ancientHistory);
    }
    CurrentState.refresh();
}
function startMove() {
    Moving = true;
    $("#items").html('<ul id="items-list"> </ul>'); // TODO: there has to be a simpler way
    if (CurrentState != null)
        $(CurrentState.nav_id).removeClass('selected');
    Buttons.addClass('Limbo');
}
function endMove() {
    Moving = false;;
    $('#nav-' + CurrentState.name).addClass('current');
    Buttons.removeClass('Limbo');
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
