// JavaScript Document
$(document).ready(function($) {
	var config = {
		'select:not([multiple="multiple"])'           : {},
		'select-deselect'  : {allow_single_deselect:true},
		'select-no-single' : {disable_search_threshold:10},
		'#select-no-results': {no_results_text:'Oops, nothing found!'},
		'#select-width'     : {width:"95%"}
	}
	for (var selector in config) {
		$(selector).chosen(config[selector]);
	}
});