// Document ready
$(document).ready(function(){
	console.log($('body > div.row').outerWidth());
	console.log($('body > div.row').outerWidth(true));
	console.log($('body > div.row').offset().left);

	// Initialize foundation
	$(document).foundation();

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
	
	// Slides
    $('.slides').slidesjs({
        width: 450,
        height: 253,
        pagination: {
            active: false
        }
    });
	
	// Go to search
	$('a.goto_search').click(function(){
		// Scroll to top
		$('body').animate({ scrollTop: 0 }, 'slow');

		// Focus search field
		$('input#search').focus();
	});

	// Initialize map
	MAP.initialize($('div#map'));

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

	// // Expand scene map
	// $('img.floater').click(function(){
	// 	var floater = $(this);
	// 	var shots = floater.parent();
	// 	var shot = shots.find('img.shot');

	// 	var shot_src = shot.attr('src');
		
	// 	shot.attr('src', floater.attr('src'));
	// 	floater.attr('src', shot_src);
 //  	});
});


// Equalize row height
function equalizeColumns() {
	//		TODO: only when two columns!
	// $('div#content > div.row > div.columns:odd, div.row.equal > div.columns:odd').each(function(){
	$('div.row.equal > div.columns:odd').each(function(){
		console.log('------ROW------');
		console.log($(this).parent()[0]);

		var even 		= $(this).prev();
		var even_column	= even.attr('class');
		var even_child 	= even.find(':first-child').attr('class');
		var even_height = even.height();

		var odd 		= $(this);
		var odd_column	= odd.attr('class');
		var odd_child 	= odd.find(':first-child').attr('class');
		var odd_height 	= odd.height();

		console.log(' - Column: ' + even_column + ' | ' + odd_column);
		console.log(' - Child: ' + even_child + ' | ' + odd_child);
		console.log(' - Height: ' + even_height + ' | ' + odd_height);

		// Resize
		// if (even_height > odd_height)
			// odd.height(even_height);

		if (odd_height < even_height)
			odd.height(even_height);

		if (odd.parent().hasClass('force'))
			if (odd_height > even_height)
				odd.height(even_height);

		console.log(' - Adjusted: ' + $(this).prev().height() + ' | ' + $(this).height());
	});
}

// Window load
$(window).load(function(){
	equalizeColumns();
});

// Window resize
$(window).resize(function(){
	equalizeColumns();
});