/*  NORLOC MAP
  ================================================================================== */

var mapTileLayers = {
	nldark: L.tileLayer('https://api.mapbox.com/styles/v1/slekvak/cjly2r5d14zbm2rlxq8elklvk/tiles/{z}/{x}/{y}?access_token={accessToken}', {
		id: 'mapbox.dark',
		name: 'Standard',
		accessToken: 'pk.eyJ1Ijoic2xla3ZhayIsImEiOiJjaXE4azdndnQwMDQ4aHhrcWZpM25rcDMxIn0.5ObHw68HeWzfLprlb5M5HA',
		attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
		maxZoom: 19,
		tileSize: 512,
		zoomOffset: -1,
	}),
	mapbox: L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
		id: 'streets-v9',
		name: 'Mapbox',
		accessToken: 'pk.eyJ1Ijoic2xla3ZhayIsImEiOiJjaXE4azdndnQwMDQ4aHhrcWZpM25rcDMxIn0.5ObHw68HeWzfLprlb5M5HA',
		attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
		maxZoom: 19,
		tileSize: 512,
		zoomOffset: -1,
	}),
	mapbox_outdoors: L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
		id: 'outdoors-v9',
		name: 'Mapbox (Outdoors)',
		accessToken: 'pk.eyJ1Ijoic2xla3ZhayIsImEiOiJjaXE4azdndnQwMDQ4aHhrcWZpM25rcDMxIn0.5ObHw68HeWzfLprlb5M5HA',
		attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
		maxZoom: 19,
		tileSize: 512,
		zoomOffset: -1,
	}),
	satellite: L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
		id: 'satellite-streets-v9',
		name: 'Satellitt',
		accessToken: 'pk.eyJ1Ijoic2xla3ZhayIsImEiOiJjaXE4azdndnQwMDQ4aHhrcWZpM25rcDMxIn0.5ObHw68HeWzfLprlb5M5HA',
		attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
	    maxZoom: 18,
	    tileSize: 512,
		zoomOffset: -1,
	}),
	norgeskart: L.tileLayer('http://opencache.statkart.no/gatekeeper/gk/gk.open_gmaps?layers=topo4&zoom={z}&x={x}&y={y}', {
		name: 'Norgeskart',
		attribution: '<a href="http://www.kartverket.no/">Kartverket</a>'
	})
};


// NorlocMap
L.Map.NorlocMap = L.Map.extend({
	// Options
	default_options: {
		layers: [mapTileLayers.nldark],
		editMode: false
	},

	// Feature groups
	featureGroups: {
		locations: L.featureGroup(),
		shots: L.featureGroup(),
	},

	// Initialize
	initialize: function (id, options) {
		// Super
		L.Util.setOptions(this, this.default_options);
		L.Map.prototype.initialize.call(this, id, options);

		UTIL.log('Initializing map, center={0}, zoom={1}, edit={2}'.format(
			this.options.center, this.options.zoom, this.options.editMode
		));

		// Add feature groups
		for (var group in this.featureGroups) { 
    		this.featureGroups[group].addTo(this);
		}

		// Controls
		L.control.layers({
		    'Standard': mapTileLayers.nldark,
		    'Satellitt': mapTileLayers.satellite,
		    'Norgeskart': mapTileLayers.norgeskart,
		    'Mapbox': mapTileLayers.mapbox,
		    'Mapbox (Outdoors)': mapTileLayers.mapbox_outdoors,
		}, {
		    'Lokasjoner': this.featureGroups.locations,
		    'Scener': this.featureGroups.shots,
		}).addTo(this);

		L.easyButton('zmdi zmdi-gps-dot', function(btn, map) {
	    	// Fit bounds
	    	map.closeModal();
			map.fitBounds(map.featureGroups.locations.getBounds());
		}, 'Zoom til alle').addTo(this);

		L.easyButton('zmdi zmdi-flare', function(btn, map) {
			// Fly to "random" location
			map.closeModal();
	    	let locations = map.featureGroups.locations.getLayers();
	    	let location = locations[Math.floor(Math.random() * locations.length)];
	    	let bounds = location.getBounds();

	    	if (bounds.length > 0) {
	    		map.flyToBounds(bounds, {maxZoom: 17});
	    		map.once('moveend', function() {
	    			location.fireEvent('click');
				});
	    	}
		}, 'Vis tilfeldig').addTo(this);

		// Events
		this.on('baselayerchange', this.onBaseLayerChange);
	},

	// Toggle edit mode
	toggleEditMode: function() {
		UTIL.log('Toggling map edit mode, enabled={0}'.format(this.options.editMode));

		if (!this.options.editMode) {
			this.options.editMode = true;
			this.featureGroups.editableGroup = L.featureGroup();
			this.featureGroups.editableGroup.addTo(this);

			// Edit controls
			L.Browser.touch = false;
			L.EditToolbar.Delete.include({
				removeAllLayers: false
			});

			this.drawControl = new L.Control.Draw({
				edit: {
					featureGroup: this.featureGroups.editableGroup,
					poly: { allowIntersection: false }
				},
				draw: {
					marker: true,
					circle: false,
					circlemarker: false,
					polyline: false,
					rectangle: false,
					polygon: {
						allowIntersection: false,
						showArea: true,
						shapeOptions: { weight: 3 }
					},
				}
			});

			// Add draw control to map instance
			this.addControl(this.drawControl);

			// Events
			this.on('draw:edited', this.onDrawEdited);
			this.on(L.Draw.Event.CREATED, this.onDrawCreated);
			this.on('draw:deleted', this.onDrawDeleted);
			this.on('draw:editstop', this.onDrawStopped);
		} 
		else {
			this.options.editMode = false;

			// Trigger cancel (hack..)
			$('a.leaflet-draw-edit-edit')[0].click()

			var editToolbarButtons = $('.leaflet-draw-actions').find('a');
			
			if (editToolbarButtons.length >= 2) {
				editToolbarButtons[1].click();
			}

			// Remove edit controls
			if (this.drawControl)
				this.removeControl(this.drawControl);

			// Unbind events
			this.off(L.Draw.Event.CREATED);
			this.off('draw:edited');
			this.off('draw:editstop');
		}
	},

	// Event: Base layer change
	onBaseLayerChange: function(event) {
		UTIL.log('map:baselayerchange - name={0}'.format(
			event.layer.options.name
		));

		// 	if (e.name === 'Satellitt') {
		// 		this.locationsGroup.setStyle(this.styles.SATELLITE);
		// 	} else {
		// 		this.locationsGroup.setStyle(this.styles.DEFAULT);
		// 	}
	},

	// Event: Draw created
	onDrawCreated: function(event) {
		UTIL.log('map:draw_created - type={0}'.format(event.layerType));

	    var created_layer = event.layer;
	    
	    created_layer.addTo(this.featureGroups.locations);

		// Type: Location polygon
	    if (event.layerType === 'polygon') {
	    	// Get bounds of created polygon
	    	var created_bounds = created_layer.getLatLngs()[0];

	    	UTIL.log('Creating location polygon, points={0}'.format(
	    		created_bounds.length
	    	));

			// Show location select modal
			var map = this;
			var source = $('#location-select-edit-template').html();
		    var template = Handlebars.compile(source);

	    	map.fire('modal', {
				content: 'Laster inn...',
				closeTitle: 'Lukk',
				INNER_CONTENT_CLS: 'modal-inner location-select',

				onShow: function(evt) { 
					// Get location details
					$.getJSON('/json/locations/', function(result) {
						// Set modal content
						var rendered = template(result);
						evt.modal.setContent(rendered);
						var content = $(evt.modal.getContentContainer());

						content.find('button[name="select_location"]').on('click', function(e) {
							// Close modal
							map.closeModal();

							// Create location polygon
							var locationId = content.find('select[name="location"]').val();
							var locationAddress = content.find('select[name="location"] option:selected').text();

			                var polygon = new L.Polygon.LocationPolygon(created_bounds, {
			                    locationId: locationId,
			                    locationAddress: locationAddress,
			                }).addTo(map.featureGroups.locations);

							polygon.updateBounds(polygon.getBounds());
						});
					});
				},

				onHide: function(evt) {
					// Remove initially created layer
					created_layer.remove();
				},
			});
	    }
	},

	// Event: Draw edited
	onDrawEdited: function(event) {
		UTIL.log('map:draw_edited');

		// Update layers
		event.layers.eachLayer(function(layer) {
			layer.updateBounds(layer.getLatLngs()[0]);
		});
	},

	// Event: Draw deleted
	onDrawDeleted: function(event) {
		UTIL.log('map:draw_deleted');

		// // Delete polygons
		// event.layers.eachLayer(function(layer) {
		// 	console.log(layer);
		// 	console.log(layer.getBounds())
		// 	layer.updateBounds([]);
		// });
	},

	// Event: Draw stopped
	onDrawStopped: function(event) {
		UTIL.log('map:draw_stopped');

		// Set all layers not editable
		this.featureGroups.editableGroup.eachLayer(function(layer) {
			layer.setEditable(false);
		});
	},
});



// LocationPolygon
L.Polygon.LocationPolygon = L.Polygon.extend({
	// Options
	default_options: {
		locationId: 0,
		locationAddress: '',
		editable: false,
	},

	// Initialize
	initialize: function(latlngs, options) {
		// Super
		L.Util.setOptions(this, this.default_options);
		L.Polygon.prototype.initialize.call(this, latlngs, options);

		// Default style
		this.setStyle({
			color: '#db3b61',
			weight: 2,
			opacity: 0.8,
			fillOpacity: 0.2,
		});

		// Events
		this.on('click', this.onClick);

		// Tooltip
		this.setTooltip(this.options.locationAddress);
	},

	// Set tooltip
	setTooltip: function(label) {
		if (!label)
			return;

		this.bindTooltip(label);
		/*polygon.bindTooltip(label,  {
			permanent: true, className: "my-label", offset: [0, 0] 
		});*/
	},

	// Set editable
	setEditable: function(editable) {
		if (editable && this._map.options.editMode) {
			this.options.editable = true;

			// Add to editable layers 
			var editablePolygon = this;
			var layer_groups = this._map.featureGroups;

			layer_groups.locations.removeLayer(this);
			
			editablePolygon.setStyle({
				color: '#03a9f4',
				weight: 2,
				opacity: 0.3,
				fillOpacity: 0.1,
			});

			editablePolygon.addTo(layer_groups.editableGroup);
		}
		else {
			this.options.editable = false;

			// Move to locations layer
			var edited_polygon = this;
			var layer_groups = this._map.featureGroups;

			layer_groups.editableGroup.removeLayer(this);

			edited_polygon.setStyle({
				color: '#db3b61',
				weight: 2,
				opacity: 0.8,
				fillOpacity: 0.2,
			});

			edited_polygon.addTo(layer_groups.locations);
		}
	},

	// Get bounds
	getBounds: function() {
		return this.getLatLngs()[0];
	},

	// Update location bounds
	updateBounds: function(bounds) {
		if (this.options.locationId == 0) {
			UTIL.log('Ignored polygon, invalid location id'.format(
				this.options.locationId
			));
			return;
		}

		if (!bounds || bounds.length < 3) {
			UTIL.log('Polygon update failed, undefined or invalid bounds ({0} points)'.format(
				bounds.length
			));
			return;	
		}

		UTIL.log('Saving location bounds {0} ({1} points)'.format(
			this.options.locationId, bounds.length
		));

		console.log(bounds);
		
		UTIL.post_json('/json/location/{0}/bounds/update'.format(this.options.locationId), bounds);
	},

	// Event: Click
	onClick: function(event) {
		if (this._map.options.editMode) {
			// Toggle editable
			this.setEditable(!this.options.editable);
		} 
		else {
			// Show location modal
			var layer = this;
			var source = $('#location-details-template').html();
		    var template = Handlebars.compile(source);

	    	this._map.fire('modal', {
				content: 'Laster inn...',
				closeTitle: 'Lukk',
				positioned: true,

				onShow: function(evt) { 
					// Get location details
					$.getJSON('/json/location/{0}/details'.format(layer.options.locationId), function(location) {
						// Set modal content
						evt.modal.setContent(template(location));
					});
				},
			});
		}

		UTIL.log('map:location_polygon:click - id={0}, editable={1}'.format(
			this.options.locationId, this.options.editable
		));
	},
});


// ShotMarker
L.Marker.ShotMarker = L.Marker.extend({
	// Options
	default_options: {
		shotId: 0,
		production: '',
		editable: false,
	},

	// Initialize
	initialize: function(latlng, options) {
		// Super
		L.Util.setOptions(this, this.default_options);
		L.Marker.prototype.initialize.call(this, latlng, options);

		// Events
		this.on('click', this.onClick);

		// Tooltip
		this.setTooltip(this.options.production);
	},

	// Set tooltip
	setTooltip: function(label) {
		if (!label)
			return;

		this.bindTooltip(label);
	},

	// Clicked
	onClick: function(event) {
		UTIL.log('map:shot_marker:click - id={0}, editable={1}'.format(
			this.options.shotId, this.options.editable
		));
	},
});