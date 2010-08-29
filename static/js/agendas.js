//SETTING UP OUR POPUP
//0 means disabled; 1 means enabled;
var popupStatus = 0;  


jQuery(document).ready(function() {

	$("#radioset").buttonset();
	// LOADING POPUP
	// Click the button event!
	$(".agendavote").click(function() {
		// centering with css
		centerPopup();
		// load popup
		loadPopup($(this).attr("agenda_name"),$(this).attr("agenda_id"),$(this).attr("vote_id"));
	});

	// CLOSING POPUP
	// Click the x event!
	$("#popupContactClose").click(function() {
		disablePopup();
	});
	// Click out event!
	$("#backgroundPopup").click(function() {
		disablePopup();
	});
	// Press Escape event!
	$(document).keypress(function(e) {
		if (e.keyCode == 27 && popupStatus == 1) {
			disablePopup();
		}
	});  

	
	
/*	$("#agendas-choose").html('');
    $.getJSON('/api/agenda/', show_your_agendas_list_callback );*/
});

/*function refresh_your_agendas_list(user_id) {
	$("#agendas-choose").html('');
	$.getJSON('/api/agenda/user/'+user_id, refresh_your_agendas_list_callback );
}*/

/*function show_your_agendas_list_callback(agendas) {
    $.each(agendas, function(i,agenda){
            var href = "javascript:ascribe_agenda("+agenda.id+");";
            $('<a class="item dontwrap">').attr("id", "agenda_"+agenda.id).attr("href", href).html(agenda.name).appendTo("#agendas-choose");
          });
    //$("#tagging-container").append("ZZZZZZZZZZZZZZZZZZZZZZZZZ" + window.location.pathname.split('/')[1] + '/' + window.location.pathname.split('/')[2])
    $.getJSON('/api/agenda/'+window.location.pathname.split('/')[1]+
        '/'+window.location.pathname.split('/')[2]+'/', mark_selected_agendas);
}

function mark_selected_agendas(agendas){
    $.each(agendas, function(i,agenda){
        $("#agenda_"+agenda.id).addClass("selected");    
    });
}*/

/*function ascribe_agenda(agenda_id) {
    //$.post("suggest-tag/", { agenda_id: agenda_id }, suggest_agenda_callback );
	if ($("#agenda_"+agenda_id).hasClass("selected")) {
	    $("#agenda_"+agenda_id).removeClass("selected");*/
/*	    $.post('/api/agenda/'+window.location.pathname.split('/')[1]+
	            '/'+window.location.pathname.split('/')[2]+'/','remove')*/
/*	    $.post('/agenda/'+agenda_id+'/ascribe-to-vote/'+window.location.pathname.split('/')[2]+'/',{},suggest_agenda_callback)
	} else {
	    $("#agenda_"+agenda_id).addClass("selected");
	    $.post('/agenda/'+agenda_id+'/ascribe-to-vote/'+window.location.pathname.split('/')[2]+'/',{},suggest_agenda_callback)
	}
}

function suggest_agenda_callback(data) {
}

function refresh_vote_agendas_list() {
	$.getJSON('/api/agenda/vote/'+window.location.pathname.split('/')[2]+'/', refresh_vote_agendas_list_callback );
}

function refresh_vote_agendas_list_callback(agendas) {
}

function open_agendavote_form(vote_id, agenda_id) {
	return false
}*/









//loading popup with jQuery magic!
function loadPopup(agenda_name,agenda_id,vote_id){  
//	loads popup only if it is disabled
	if(popupStatus==0){  
		$(".popup h1").html(agenda_name)
		$("#backgroundPopup").css({  
			"opacity": "0.7"  
		});  
		$("#backgroundPopup").fadeIn("slow");  
		$("#popupContact").fadeIn("slow");  
		popupStatus = 1;  
	}  
}  


//disabling popup with jQuery magic!
function disablePopup(){  
//	disables popup only if it is enabled
	if(popupStatus==1){  
		$("#backgroundPopup").fadeOut("slow");  
		$("#popupContact").fadeOut("slow");  
		popupStatus = 0;  
	}  
}  

//centering popup
function centerPopup(){  
//	request data for centering
	var windowWidth = document.documentElement.clientWidth;  
	var windowHeight = document.documentElement.clientHeight;  
	var popupHeight = $("#popupContact").height();  
	var popupWidth = $("#popupContact").width();  
//	centering
	$(".popup #popupContact").css({  
		"position": "absolute",  
		"top": windowHeight/2-popupHeight/2,  
		"left": windowWidth/2-popupWidth/2  
	});  
//	only need force for IE6

	$(".popup #backgroundPopup").css({  
		"height": windowHeight  
	});  

}  


