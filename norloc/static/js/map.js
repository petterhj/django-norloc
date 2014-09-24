// 	Map
// ===========================================================================

var MAP = MAP || {
	// Instance
	instance: null,
	overlay: null,

	// Options
	options: {
		center: 	new google.maps.LatLng(60.397, 11.644),
		zoom:   	14,
		styles: 	style_grey
	},

	// Bounds
	bounds: new google.maps.LatLngBounds(),

	// Locations
	locations: [],

	// Shots
	shots: [],

	// Canvas
	canvas: {
		container: $('<div>', {id: 'paper_canvas'}),
		paper: null
	},

	// Initialize map
	initialize: function(container) {
		if ((container !== undefined) && (container.length)) {
			// Create map
			this.instance = new google.maps.Map(container[0], this.options);

			// Get data
			this.log('Fetching location data');

			$.getJSON('/locations/?api=json', function(data) {
				MAP.log('Done fetching data');

				// Locations
		  		$.each(data, function(k, location) {
		  			if (location.bounds.length > 2) {
	  					// Polygon
	  					var points = [];

						$.each(location.bounds, function(k, point) {
							points.push(new google.maps.LatLng(point.latitude, point.longitude));
						});

		  				var area = new google.maps.Polygon({
		  					title: 			location.address,
	    					paths: 			points,
	    					strokeColor: 	'#3FB06B',
	    					strokeOpacity: 	0.6,
	    					strokeWeight: 	2,
	    					fillColor: 		'#3FB06B',
	    					fillOpacity: 	0.25,
	    					map: 			MAP.instance
	  					});

	  					MAP.locations.push(area);
	  				}

		  			// Scenes
		  			$.each(location.scenes, function(k, scene) {
		  				// Shots
		  				$.each(scene.shots, function(j, shot) {
			  				// Point
			  				if ((shot.latitude != null) && (shot.longitude != null)){
				  				var point = new google.maps.LatLng(shot.latitude, shot.longitude);

			          			MAP.bounds.extend(point);

				    			// Marker
				    			var marker = new RichMarker({
						    		title: 		scene.production.title,
						    		animation: 	google.maps.Animation.DROP,
						    		position: 	point,
						    		anchor: 	RichMarkerPosition.MIDDLE,
						    		flat: 		true,
			          				content: 	'<img src="/static/img/bullet_blue.png" alt="symbol" title="' + scene.production.title + ' (' + scene.production.year + ')">',
						    		map: 		MAP.instance
			          			});

			          			marker.slug = scene.production.slug;
			          			marker.year = scene.production.year;

				    			// Click event
								google.maps.event.addListener(marker, 'click', function() {
									MAP.removeHighlight();
									MAP.productionHighlight(marker);
		  						});

			          			MAP.shots.push(marker);
			          		}
		          		});
	    			});
	    		});

				MAP.log(' > ' + MAP.locations.length + ' locations added');
				MAP.log(' > ' + MAP.shots.length + ' scene shots added');

				// Fit to bounds
				MAP.fitBounds();
		  	});

			// Reset highlight
			google.maps.event.addListener(this.instance, 'click', function(event) {
				MAP.removeHighlight();
			});

			// Overlay
			this.overlay = new google.maps.OverlayView();
			this.overlay.draw = function() {};
			this.overlay.setMap(this.instance);

			// Canvas
			this.canvas.container.appendTo(container);
			this.canvas.paper = Raphael(this.canvas.container[0]);
			this.canvas.container.hide();

			// Return
			return this;
		}
		else {
			this.log('Undefined container');
		}
	},

	// Fit bounds
	fitBounds: function(bounds) {
		if (bounds === undefined)
			bounds = this.bounds;

		// Fit to provided bounds
		MAP.log('[BOUNDS] ' + this.bounds);
		this.instance.fitBounds(this.bounds);
	},

	// Show overlays
	showOverlays: function() {
		if (this.instance) {

		}
	},

	// Hide overlays
	hideOverlays: function() {
		//
		//
	},

	// Production highlight
	productionHighlight: function(marker) {
		if ((marker !== undefined) && (this.instance)) {
			// Highlight production specific markers
			$.each(MAP.shots, function(j, shot) {
				if(shot.slug != marker.slug)
					shot.setContent('<img src="/static/img/bullet_grey.png" alt="symbol" title="' + shot.title + ' (' + shot.year + ')">');
			});

			// Get data
			this.log('Fetching production data');

			$.getJSON('/productions/production/' + marker.slug + '?api=json', function(data) {
				MAP.log('Done fetching data');

				// Locations
				var locations = $('<div>', {class: 'locations'});

		  		$.each(data.locations, function(k, location) {
		  			// Location
		  			var loc = $('<div>', {class: 'location'}).append($('<span>').text(location.address));

		  			$.each(location.scenes, function(j, scene) {
		  				// Scene
		  				var sc = $('<div>', {class: 'scene'});

		  				// Shots
		  				$.each(scene, function(j, shot) {
							// Shots
							sc.append($('<img>', {class: 'shot', src: shot.url})
								// Toggle arrow
								.hover(function() {
									// Position
									var point = MAP.overlay.getProjection().fromLatLngToContainerPixel(new google.maps.LatLng(shot.latitude, shot.longitude));

									var strt = {
										x: (($(this).offset().left - $('div#map').offset().left) + ($(this).width() / 2)),
										y: MAP.canvas.container.height()
									};
									var dest = {
										x: Math.round(point.x),
										y: Math.round(point.y)
									}

									// Animate arrow
									MAP.canvas.container.show();
        							MAP.canvas.paper.path().attr({path: 'M' + strt.x + ',' + strt.y + ' L' + strt.x + ',' + strt.y, stroke: '#333'})
        								.stop()
        								.animate({path: 'M' + strt.x + ',' + strt.y + ' L' + dest.x + ',' + dest.y}, 500);
							  	}, function() {
							  		// Clear canvas
							    	MAP.canvas.paper.clear();
							    	MAP.canvas.container.hide();
							  	})	
							)
		  				});

		  				loc.append(sc);
		  			});

		  			locations.append(loc);
		  		});

				// Production overlay
				var overlay = $('<div>', {class: 'overlay production'})
					// Poster
					.append($('<img>', {class: 'poster', src: data.poster, title: data.title + ' (' + data.year + ')'}).click(function(){ window.location = '!'; }))

					// Locations
					.append(locations);


				// Display overlay
				overlay.hide().appendTo(MAP.instance.getDiv()).fadeIn('slow');

				// Enable scrolling
				$('div.locations', overlay).niceScroll({
					cursorborder: 		'0',
					cursorcolor: 		'#666',
					bouncescroll: 		true,
					cursorborderradius: '0',
					cursorwidth: 		'3px'
				});
		  	});
		}
		else {
			this.log('Could not display highlight');
		}
	},

	// Pinpoint shot marker

	// Remove 
	removeHighlight: function() {
		// Reset markers
		$.each(MAP.shots, function(j, shot) {
			shot.setContent('<img src="/static/img/bullet_blue.png" alt="symbol" title="' + shot.title + ' (' + shot.year + ')">');
		});

		// Fade out
		$('div.overlay', this.instance.getDiv()).fadeOut('slow', function() {
			// Remove
			$(this).remove();
		});
	},

	// Logging
	log: function(string) {
		console.log('[MAP] ' + string);
	}
};