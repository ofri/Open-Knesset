//SETTING UP OUR POPUP
//0 means disabled; 1 means enabled;
var popupStatus = 0;
var popup_agenda_id = -1;
var popup_vote_id = -1;
var popup_agenda_marked = -1;
var vote_info


jQuery(document).ready(function() {

	// LOADING POPUP
	// Click the button event!
	$(".agendavote").click(function() {
		// centering with css
		centerPopup();
		// load popup
		is_agenda_marked = $(this).hasClass("selected")
		loadPopup($(this).attr("agenda_name"), $(this).attr("agenda_id"),
				  $(this).attr("vote_id"), is_agenda_marked);
	});

	// User click on submit button
	$("#popupContactClose").click(function() {
		disablePopup();
		window.location.replace(".");
	});

	$(".popup label").click(function () {
		if ($(this).attr("id") == 'ascribe') {
    		$.post("/agenda/"+popup_agenda_id+"/vote/"+popup_vote_id+"/", {action: $(this).attr("id")}, function(data){
			    popup_agenda_marked = true;
			    vote_info = data;
			    $("#agenda-vote-compliance-radioset #aradio3").attr("checked","checked");
			    $("#agenda-vote-compliance-radioset").button("refresh");
    		});
		} else {
    		$.post("/agenda/"+popup_agenda_id+"/vote/"+popup_vote_id+"/", {action: $(this).attr("id")});
		
		}
		if ($(this).attr("id") == 'remove') {
			popup_agenda_marked = false;
		}
	});
	
	// partialy
	getVoteInfo();
});

function getVoteInfo() {
	$.get("/api/vote/"+window.location.pathname.split('/')[2]+"/", function(data) {
		vote_info = data;
	})
}

//loading popup with jQuery magic!
function loadPopup(agenda_name, agenda_id, vote_id, is_agenda_marked){  
//	loads popup only if it is disabled
	if(popupStatus==0){  
		popup_agenda_id = agenda_id;
		popup_vote_id = vote_id;
		popup_agenda_marked = is_agenda_marked;
		var agenda = vote_info.agendas[agenda_id];
		if (popup_agenda_marked) {
			$("#ascribe-agenda-radioset #radio1").attr("checked","checked");
			$(".popup #reasoning").html(agenda.reasoning);
			$("#agenda-vote-compliance-radioset #"+$(".popup #"+agenda.text_score).attr("for")).attr("checked","checked");
		} else {
			$("#ascribe-agenda-radioset #radio2").attr("checked","checked");
		}
		
		$("#ascribe-agenda-radioset").buttonset();
		$("#agenda-vote-compliance-radioset").buttonset();

		$(".popup h1").html(agenda_name);
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
		if (popup_agenda_marked) {
			updated_reasoning = $(".popup #reasoning").attr("value");
			if (updated_reasoning != vote_info.agendas[popup_agenda_id].reasoning) {
				$.post("/agenda/"+popup_agenda_id+"/vote/"+popup_vote_id+"/", {action: 'reasoning', reasoning: updated_reasoning});
			}
		}
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
