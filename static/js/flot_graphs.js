var graph;
var all_data = null;

function showTooltip(x, y, contents) {
    $('<div id="tooltip">' + contents + '</div>').css( {
        position: 'absolute',
        display: 'none',
        top: y + 5,
        left: x + 5,
        border: '1px solid #fdd',
        padding: '2px',
        'background-color': '#fee'
    }).appendTo("body").fadeIn(100);
};

function sortNumber(a, b)
{
    return a - b;
}

function load_data_callback(original_data){
    all_data = original_data;
    $(".axis_combobox").html('<select><option value="discipline">משמעת</option><option value="service_time">זמן בכנסת ה-18</option><option value="votes_count">כמות הצבעות</option><option value="votes_per_month">ממוצע הצבעות בחודש</option><option value="average_weekly_presence">ממוצע שעות נוכחות שבועיות</option></select>')    
    $("#y-axis>select").val('votes_per_month');
    $(".axis_combobox").change(function() {
        update_graph(all_data);
    });
    update_graph(original_data);
}

function update_graph(original_data){
    var parties = {};
    var minx = 1E100;
    var maxx = -1E100;
    var miny = 1E100;
    var maxy = -1E100;
    var values1 = [];
    var values2 = [];
    var var1_name = $('#x-axis>select').val()
    var var2_name = $('#y-axis>select').val()
    for(var i=0;i<original_data.length;i++){
        party = original_data[i]['party'].replace(/ /g,'_');
        var name = original_data[i]['name'];
        var var1 = original_data[i][var1_name];
        
        if (var1>maxx)
            maxx = var1;
        if (var1<minx)
            minx = var1;
        var var2 = original_data[i][var2_name];
        if ((var1!=null)&(var2!=null)){        
            values1.push(var1);        
            values2.push(var2);
            if (var2>maxy)
                maxy = var2;
            if (var2<miny)
                miny = var2;
            var image_url = original_data[i]['img_url'];
            if (!(party in parties)) {
                parties[party] = {names:[],raw_data:[],data:[],image_url:[]};            
            }
            parties[party].names.push(name);
            parties[party].raw_data.push([var1,var2]);
            parties[party].image_url.push(image_url);
        };
    };
    values1.sort(sortNumber);
    values2.sort(sortNumber);
    var scale1 = [values1[0]];
    var scale2 = [values2[0]];
    for (var i=1;i<values1.length/10;i++){
        if (values1[i*10]>scale1.slice(-1))
            scale1.push(values1[i*10]);
        if (values2[i*10]>scale2.slice(-1))
            scale2.push(values2[i*10]);
    }
    if (values1.slice(-1)>scale1.slice(-1))
        scale1.push(values1.slice(-1));
    if (values2.slice(-1)>scale2.slice(-1))
        scale2.push(values2.slice(-1));

    var k;
    var alpha;
    for (var i in parties){
        for (var j=0;j<parties[i].raw_data.length;j++){
            var var1 = parties[i].raw_data[j][0];
            var var2 = parties[i].raw_data[j][1];            
            for (k=0; k<scale1.length-1 & scale1[k]<=var1;k++){};
            alpha = (var1-scale1[k-1])/(scale1[k]-scale1[k-1]);
            var1 = k*(alpha)+(k-1)*(1-alpha);
            for (k=0; k<scale2.length-1 & scale2[k]<=var2;k++){};
            alpha = (var2-scale2[k-1])/(scale2[k]-scale2[k-1]);
            var2 = k*(alpha)+(k-1)*(1-alpha);
            parties[i].data.push([var1,var2]);
        };
    };
    var data = [];
    for (var i in parties){
      data.push({label:i, data:parties[i].data});
    };
                        
    graph = $.plot($("#placeholder"), data, 
      {   
        legend: {
            container: $("#legend"),
            noColumns: 6,
            labelFormatter: function(a,b){return '<a class="party_link" "href="#">'+a.replace(/_/g," ")+'</a>'}
          },

       series: {
            lines: { show: false },
            points: { show: true }
         },
        points: {
            radius: 4,
            fill: false
        },
        shadowSize: 2,
         xaxis: { ticks: [ [0, scale1[0].toString()], [(scale1.length-1)/2, 'average '+var1_name.replace(/_/g,' ')],[scale1.length-1, scale1.slice(-1).toString()] ] },
//                  transform: function (v) { return Math.log(v); },
//                  inverseTransform: function (v) { return Math.exp(v); }
                    
       //         },
         yaxis: { ticks: [ [0, scale2[0].toString()], [(scale2.length-1)/2, 'average<br/>'+var2_name.replace(/_/g,' ')],[scale2.length-1, scale2.slice(-1).toString()] ] },
//                  transform: function (v) { return Math.log(v); },
//                  inverseTransform: function (v) { return Math.exp(v); }
       //         }, 
         grid: { tickColor: 'black', backgroundColor: { colors: ["#fff", "#ddd"] }, hoverable: true, clickable: true,
               }
    
       }
    );

    var previousPoint = null;

    $("#placeholder").bind("plothover", function (event, pos, item) {
        //$("#x").text(pos.x.toFixed(2));
        //$("#y").text(pos.y.toFixed(2));


            if (item) {
                if (previousPoint != item.datapoint) {
                    previousPoint = item.datapoint;
                    
                    $("#tooltip").remove();
                    //var x = item.datapoint[0].toFixed(2),
                    //    y = item.datapoint[1].toFixed(2);
                    var party = item.series.label;
                    var d = parties[party].raw_data[item.dataIndex];
                    showTooltip(item.pageX, item.pageY,
                                 parties[party].names[item.dataIndex] + '<br/>('+party.replace(/_/g,' ')+')‏<br/>'+var1_name.replace(/_/g,' ')+': '+d[0]+'<br/>'+var2_name.replace(/_/g,' ')+': '+d[1]+'<br/><img src="'+parties[party].image_url[item.dataIndex]+'"/>');
                }
            }
            else {
                $("#tooltip").remove();
                previousPoint = null;            
            }
    });

    $(".party_link").hover(
          function () {
            var party = $(this).html().replace(/ /g,'_');            
            for (var d=0; d<data.length; d++){
                if (data[d].label==party){
                    for(var j=0;j<data[d].data.length;j++)
                        graph.highlight(d,j);
                };
            }

          }, 
          function () {
            graph.unhighlight();
          }
    );

}

$(document).ready(function () {
    $("#placeholder").html('Loading Data');
    $.getJSON('/api/member/', load_data_callback );
});

