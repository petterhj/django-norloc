/*  NORLOC MAP
  ================================================================================== */

var LocationPolygon = L.Polygon.extend({
	options: {
		locationId: 0,
		locationAddress: '',
	}
});


// Norloc map
function NLMap(container, center, zoom) {
	UTIL.log('Initializing map');

	// Properties
	this.container = container;
	this.center = center;
	this.zoom = zoom;

	this.styles = {
		DEFAULT: {
			color: '#db3b61',
			weight: 2,
			opacity: 0.8,
			fillOpacity: 0.2,
		},
		SATELLITE: {
			color: 'red',
			weight: 3,
			opacity: 0.8,
			fillOpacity: 0,
		},
		EDITABLE: {
			color: '#f87d42',
			weight: 2,
			opacity: 0.3,
			fillOpacity: 0.1,
		},
		SELECTED: {
			color: '#be3737',
			weight: 2,
			opacity: 0.3,
			fillOpacity: 0.1,
		}
	}

	// Tile layers
	var nldark = L.tileLayer('https://api.mapbox.com/styles/v1/slekvak/cjly2r5d14zbm2rlxq8elklvk/tiles/{z}/{x}/{y}?access_token={accessToken}', {
		id: 'mapbox.dark',
		accessToken: 'pk.eyJ1Ijoic2xla3ZhayIsImEiOiJjaXE4azdndnQwMDQ4aHhrcWZpM25rcDMxIn0.5ObHw68HeWzfLprlb5M5HA',
		attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
		maxZoom: 19,
		tileSize: 512,
		zoomOffset: -1,
	});

	var mapbox = L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
		id: 'streets-v9',
		accessToken: 'pk.eyJ1Ijoic2xla3ZhayIsImEiOiJjaXE4azdndnQwMDQ4aHhrcWZpM25rcDMxIn0.5ObHw68HeWzfLprlb5M5HA',
		attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
		maxZoom: 19,
		tileSize: 512,
		zoomOffset: -1,
	});

	var mapbox_outdoors = L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
		id: 'outdoors-v9',
		accessToken: 'pk.eyJ1Ijoic2xla3ZhayIsImEiOiJjaXE4azdndnQwMDQ4aHhrcWZpM25rcDMxIn0.5ObHw68HeWzfLprlb5M5HA',
		attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
		maxZoom: 19,
		tileSize: 512,
		zoomOffset: -1,
	});

	var satellite = L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
		id: 'satellite-streets-v9',
		accessToken: 'pk.eyJ1Ijoic2xla3ZhayIsImEiOiJjaXE4azdndnQwMDQ4aHhrcWZpM25rcDMxIn0.5ObHw68HeWzfLprlb5M5HA',
		attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
	    maxZoom: 18,
	    tileSize: 512,
		zoomOffset: -1,
	});

	var norgeskart = L.tileLayer('http://opencache.statkart.no/gatekeeper/gk/gk.open_gmaps?layers=topo4&zoom={z}&x={x}&y={y}', {
		attribution: '<a href="http://www.kartverket.no/">Kartverket</a>'
	});

	// Map
	this.instance = L.map(this.container, {
		center: this.center,
		zoom: this.zoom,
		layers: [mapbox]
	});

	// Locations
	this.locationsGroup = L.featureGroup().addTo(this.instance);
	this.scenesGroup = L.featureGroup().addTo(this.instance);

	// Control
	L.control.layers({
	    'Standard': nldark,
	    'Satellitt': satellite,
	    'Norgeskart': norgeskart,
	    'Mapbox': mapbox,
	    'Mapbox (Outdoors)': mapbox_outdoors,
	}, {
	    'Lokasjoner': this.locationsGroup,
	    'Scener': this.scenesGroup,
	}).addTo(this.instance);

	L.easyButton('zmdi zmdi-gps-dot', function(btn, map) {
    	// Fit bounds
		map.fitBounds(this.locationsGroup.getBounds());
	}.bind(this), 'Zoom til alle').addTo(this.instance);

	// Tile layer change
	this.instance.on('baselayerchange', function(e) {
		if (e.name === 'Satellitt') {
			this.locationsGroup.setStyle(this.styles.SATELLITE);
		} else {
			this.locationsGroup.setStyle(this.styles.DEFAULT);
		}
	}.bind(this));

	// Editor
	this.editMode = false;
	this.drawControl = undefined;
	this.editableGroup = undefined;
	this.selectedEditable = undefined;
}

// Add location
NLMap.prototype.addLocation = function(id, bounds, label) {
	// Check bounds size
	if (bounds.length < 3) {
		UTIL.log('Ignoring location {0}:{1}, too few points defined'.format(id, label));
		return;
	}

	UTIL.log('Adding location {0}:{1} ({2} points)'.format(id, label, bounds.length));

	// Create location polygon
	var polygon = new LocationPolygon(bounds, {
		locationId: id,
		locationAddress: label,
	});

	polygon.setStyle(this.styles.DEFAULT);

	if (label) {
		polygon.bindTooltip(label);
		/*polygon.bindTooltip(label,  {
			permanent: true, className: "my-label", offset: [0, 0] 
		});*/
	}

	polygon.on('click', this.onPolygonClick.bind(this));

	polygon.addTo(this.locationsGroup);
}


// Add scene
NLMap.prototype.addScene = function(id, scene) {
	UTIL.log('Adding scene {0}'.format(id));

	// Add scene shots as markers
	var shots_coordinates = [];

	$.each(scene.shots, function(shpk, shot) {
        if (shot.coordinate) {
        	// Coordinate
        	shots_coordinates.push(shot.coordinate);

        	// Marker
			var marker = L.marker(shot.coordinate, {icon: L.divIcon({
				className: 'mapShotMarker',
				html: '<img src="{0}">'.format((shot.image ? shot.image : '/static/img/bullet_blue.png'))
			})});

			marker.addTo(this.scenesGroup);
			marker.bindPopup(scene.production);
        }
    }.bind(this));

	// Connect shots in same scene
	if (shots_coordinates.length > 1) {
    	var polyline = L.polyline(shots_coordinates, {
    		color: '#345C7C',
    		opacity: 0.3,
    		weight: 3,
    		dashArray: '1 4',
    	});

    	polyline.addTo(this.scenesGroup);
    }
}


// Toggle edit mode
NLMap.prototype.toggleEditMode = function() {
	if (!this.editMode) {
		UTIL.log('Enabling map edit mode');

		// Feature group
		this.editableGroup = L.featureGroup().addTo(this.instance);


		// Edit controls
		L.Browser.touch = false;
		L.EditToolbar.Delete.include({
			removeAllLayers: false
		});

		this.drawControl = new L.Control.Draw({
			edit: {
				featureGroup: this.editableGroup,
				poly: {
					allowIntersection: false
				}
			},
			draw: {
				marker: false,
				circle: false,
				circlemarker: false,
				polyline: false,
				rectangle: false,
				polygon: {
					allowIntersection: false,
					showArea: true,
					shapeOptions: {
						weight: 2,
					},
				},
			}
		});

		// Add draw control to map instance
		this.instance.addControl(this.drawControl);

		// Mark polygons editable
		this.locationsGroup.setStyle(this.styles.EDITABLE);

		// Bind edited event
		this.instance.on('draw:edited', function (e) {
			UTIL.log('Map event fired - draw:edited');

			// Check if any edited layers
			var layers = e.layers.getLayers();

			if (layers.length == 0) {
				UTIL.log('No changed layers')
				return;
			}
			
			// Update polygon
			var polygon = layers[0];
			// layers.eachLayer(function(layer) {});

			UTIL.log('Updating location {0} ({1} points)'.format(
				polygon.options.locationId, polygon.getLatLngs()[0].length
			));

			$.ajaxSetup({beforeSend: function(xhr, settings) {
				xhr.setRequestHeader('X-CSRFToken', UTIL.getCookie('csrftoken'));
			}});

			$.ajax({
				type: 'POST',
				dataType: 'json',
				contentType: 'application/json; charset=utf-8',
				url: '/json/location/{0}/bounds/update'.format(polygon.options.locationId),
				data: JSON.stringify(polygon.getLatLngs()[0]),
				success: function(result) {
					console.log(result);
				},
				fail: function() {
					console.log('FAIL')
				}
			});

			// Remove all editable layers
			// console.log(this.editableGroup);
			// this.editableGroup.clearLayers();
		}.bind(this));

		// Bind created event
		this.instance.on(L.Draw.Event.CREATED, function(e) {
			UTIL.log('Map event fired - draw:created');

			var type = e.layerType;
            var layer = e.layer;

            console.log(type);
            console.log(layer);


		}.bind(this));

		// Bind edit stop event
		this.instance.on('draw:editstop', function (e) {
			UTIL.log('Map event fired - draw:editstop');


		}.bind(this));

		

		this.editMode = true;

	} else {
		UTIL.log('Disabling map edit mode');

		this.editMode = false;
	}
}


// Event: Polygon click
NLMap.prototype.onPolygonClick = function(event) {
	var polygon = event.target;

	if (!this.editMode) {
		// View mode
		UTIL.log('View polygon')

	} else {
		// Set layer editable
		if (!this.selectedEditable) {
			UTIL.log('Edit polygon: {0}:{1}'.format(
				polygon.options.locationId, polygon.options.locationAddress
			));

			// Display location details
			var map = this.instance;

			$.getJSON('/json/location/{0}/details'.format(polygon.options.locationId), function(location) {
				// Template
		        var source   = $('#location-details-edit-template').html();
		        var template = Handlebars.compile(source);
		        var rendered = $(template(location));

		        rendered.on('mouseover', function () {
        			map.dragging.disable();
        			map.doubleClickZoom.disable();
        			map.scrollWheelZoom.disable();
        			map.boxZoom.disable();
    			});
		        rendered.on('mouseout', function () {
        			map.dragging.enable();
        			map.doubleClickZoom.enable();
        			map.scrollWheelZoom.enable();
        			map.boxZoom.enable();
    			});

                // Add location details control
                $('div.leaflet-control-container').append(rendered);

                // Save
                rendered.find('input[name="save"]').click(function() {
                	console.log('SAVE!');
                });
            });

			// Add to editable items 
			this.editableGroup.addLayer(polygon);

			// console.log(polygon.editable);

			// Mark as selected
			polygon.setStyle(this.styles.SELECTED);

			this.selectedEditable = polygon;

			$('a.leaflet-draw-edit-edit').trigger('click');

		} else {
			console.log('Another layer currently beeing editable')
		}
	}
}