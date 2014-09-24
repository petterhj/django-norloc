// Document ready
$(document).ready(function(){
	// Truncate
	$('.truncate').dotdotdot({
		watch: 				true,
		wrap: 				'letter'
	});

	// Scoll
	$('.scroll').niceScroll({
		cursorborder: 		'0',
		cursorcolor: 		'#666',
		bouncescroll: 		true,
		cursorborderradius: '0',
		cursorwidth: 		'3px'
	});

	// Initialize map
	MAP.initialize($('div#map'));

	// Equalize row height
	//		TODO: only when two columns!
	$('div#content > div.row > div.columns:odd').each(function(){
		console.log($(this).prev().height() + ' - ' + $(this).height());

		if ($(this).prev().height() > $(this).height())
			$(this).height($(this).prev().height());

		if ($(this).height() < $(this).prev().height())
			$(this).prev().height($(this).height());
	});

	// Tooltip: Login
	$('button.user, i.fa-user').tooltipster({
		position: 		'bottom',
		autoClose: 		true,
		interactive: 	true,
		trigger: 		'click',
		theme: 			'nl-tooltip',
		position: 		'bottom-right',
		functionReady: 	function(origin, tooltip){
			$('input[name="username"]', tooltip).focus();
		}
	})
	.click(function(){
		var tooltip = $(this);
        var tooltip_url = tooltip.hasClass('login') ? '/tooltip/login' : '/tooltip/user';

		$.get(tooltip_url, function(data){
			tooltip.tooltipster('content', $('<div>' + data + '</div>'));
		});
	});
});