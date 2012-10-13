function toggleHelpExtended() {
	$("#help-extended").toggle();
};

$(document).ready(function() {
	$("#toggle-help").click(function() {toggleHelpExtended();});
	$("#help-extended").hide();
		});