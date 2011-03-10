function set_percentile(id,value) {
        $("#"+id+"_percentile").css('background-position',((100-value))+"px 0px");
		var message;
        if ( value < 20 ) {
            message = gettext("Extremely below average");
        } else if ( value < 40 ) {
            message = gettext("Below average");            
        } else if ( value < 60 ) {
            message = gettext("Average");                
        } else if ( value < 80 ) {
            message = gettext("Above average");                
        } else {
            message = gettext("Extremely above average");
        }
		$("#"+id+"_percentile").html("<span title='"+gettext("Percentile")+" "+value+"'>"+message+"</span>"); 
	}
