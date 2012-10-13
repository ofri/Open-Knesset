function toggleHelpExtended() {
	$(".help-section-extended").toggle();
	$("#toggle-help").hide();
};

function unToggleHelpExtended() {
	$(".help-section-extended").toggle();
	$("#toggle-help").show();
};


$(document).ready(function() {
	$("#toggle-help").click(function() {toggleHelpExtended();});
	$("#un-toggle-help").click(function() {unToggleHelpExtended();});
	$(".help-section-extended").hide();
		});