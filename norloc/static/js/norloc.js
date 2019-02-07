/*  NORLOC
  ================================================================================== */

// NORLOC
var NORLOC = NORLOC || {
    // Options
    options: {
        name: 'NORLOC',
        debug: true,
        map_style: [{featureType:"all",elementType:"labels.text.fill",stylers:[{saturation:36},{color:"#000000"},{lightness:40}]},{featureType:"all",elementType:"labels.text.stroke",stylers:[{visibility:"on"},{color:"#000000"},{lightness:16}]},{featureType:"all",elementType:"labels.icon",stylers:[{visibility:"off"}]},{featureType:"administrative",elementType:"geometry.fill",stylers:[{color:"#000000"},{lightness:20}]},{featureType:"administrative",elementType:"geometry.stroke",stylers:[{color:"#000000"},{lightness:17},{weight:1.2}]},{featureType:"landscape",elementType:"geometry",stylers:[{color:"#000000"},{lightness:20}]},{featureType:"poi",elementType:"geometry",stylers:[{color:"#000000"},{lightness:21}]},{featureType:"road.highway",elementType:"geometry.fill",stylers:[{color:"#000000"},{lightness:17}]},{featureType:"road.highway",elementType:"geometry.stroke",stylers:[{color:"#000000"},{lightness:29},{weight:.2}]},{featureType:"road.arterial",elementType:"geometry",stylers:[{color:"#000000"},{lightness:18}]},{featureType:"road.local",elementType:"geometry",stylers:[{color:"#000000"},{lightness:16}]},{featureType:"transit",elementType:"geometry",stylers:[{color:"#000000"},{lightness:19}]},{featureType:"water",elementType:"geometry",stylers:[{color:"#000000"},{lightness:17}]}],
        is_authenticated: DJANGO_USER,
    },

    // View: Common
    common: function() {
        // Set placeholders as titles
        $(':text').each(function(i, input) {
            var input = $(input);
            var placeholder = input.attr('placeholder');
            if (placeholder) {
                input.attr('title', placeholder);
            }
        });
    },

    // View: Index
    index: function() {},

    // View: Production
    production: function() {
        // Template
        var source   = $('#location-template').html();
        var template = Handlebars.compile(source);

        Handlebars.registerHelper('shot_size', function(scene_count, shot_count, shot_num) {
            if ((shot_count == 1) || ((shot_count > 2) && (shot_num == 0))) {
                return 'double';
            } 
            else if ((scene_count == 1) && (shot_length == 2)) {
                return 'double';
            }
            else {
                return '';
            }
        });

        Handlebars.registerHelper('shot_size2', function(is_double, shot_count) {
            if (is_double) {
                return 'double';
            }
            if (shot_count == 1) {
                return 'double';
            }
            return '';
        });

        Handlebars.registerHelper('timecode', function(seconds) {
            // return moment.duration(seconds)//.format('HH:mm:SS');
            return moment.utc(seconds * 1000).format('HH:mm:ss');
        });
                
        // Load locations
        var ppk = $('section.content.locations').data('content-pk');

        UTIL.log('Fetching locations for production {0}'.format(ppk));

        $.getJSON('/json/production/{0}/locations/'.format(ppk), function(locations) {
            $.each(locations, function(i, location) {
                var rendered = $(template(location));
                
                $('section.content.locations').append(rendered.hide().fadeIn('slow'));

                // Map
                rendered.find('i.zmdi-map').click(function() {
                    if (rendered.find('div.map').length > 0) {
                        rendered.find('div.map').fadeOut(500).remove();
                    } else {
                        var mapc = $('<div>', {class: 'map'}).text('aad').css({
                            width: rendered.find('div.scenes').width(),
                            height: (rendered.find('div.scenes').height() - 40),
                            position: 'absolute',
                            top: '30px',
                            left: '30px',
                            background: '#CCC',
                            'border-radius': '3px'
                          });

                        rendered.append(mapc.show());

                        var map = new NLMap(mapc[0], [59.927669, 10.741541], 16);
                    }
                });
            });

            // Move add button
            $('section.content.locations').append($('div.location.add').show());
        }); 
    },

    // View: Map
    map: function() {
        var map = new NLMap('map', [59.927669, 10.741541], 16);
        
        // Locations
        $.getJSON('/json/locations/', function(locations) {
            $.each(locations, function(lpk, location) {
                map.addLocation(lpk, location.bounds, location.full_address);
            });

            // Scenes
            $.getJSON('/json/scenes/', function(scenes) {
                $.each(scenes, function(spk, scene) {
                    map.addScene(spk, scene);
                });

                // Fit bounds
                map.instance.fitBounds(map.locationsGroup.getBounds());


                ////////////////////
                map.toggleEditMode();
                ////////////////////
            });
        });

        $('i.zmdi-edit').on('click', function(e) {
            map.toggleEditMode();
        });
    },

    // View: Import production
    import_production: function() {
        // Template
        var target = $('section.content');
        var result_template = Handlebars.compile($('#production-result-template').html());

        // Search production
        // $('form[name="search_production"]').on('submit', function(e) {
            // var search_form = $(this);
            var search_form = $('form[name="search_production"]');
            var title = search_form.find('input[name="title"]').val();

            // Prevent default submit handling
            // e.preventDefault();

            if (!title) {
                return;
            }

            UTIL.log('Searching for production: {0}'.format(title))

            // Remove any previous results
            target.find('div.card.film').fadeOut(function() { $(this).remove(); })

            // Temporarily disable inputs
            search_form.find(':input').prop('disabled', true);

            // Search productions
            var dummy = {films: [{tmdb_id: 57989,poster: "http://image.tmdb.org/t/p/original/x20TMnrvelUeFd7054CJEH5wglo.jpg",imdb_id: "tt0055500",countries: {no: "Norway"},popularity: 1.341,summary: "",originaltitle: "Sønner av Norge",directors: ["Øyvind Vennerød"],release: "1961-01-01",title: "Sønner av Norge",runtime: 90},{tmdb_id: 81834,poster: "http://image.tmdb.org/t/p/original/nulCQs4WEs4lzWMABTs5kkiUgD1.jpg",imdb_id: "tt1601227",countries: {no: "Norway"},popularity: 0.777,summary: "Det er ikke lett å gjøre opprør når faren din vil være med ... En dag i 1979 møter Magnus (Sven Nordin) og Nikolaj (Åsmund Høeg) veggen i sitt nye rekkehus på Rykkinn. Far Magnus er arkitekt, hippie og fritenker, noe som skiller seg ut i et miljø der likhet og samhold er idealet. Han gir alltid sønnen ubetinget støtte - også når Nikolaj bestemmer seg for å gi faen i alt.",originaltitle: "Sønner av Norge",directors: ["Jens Lien"],release: "2011-09-08",title: "Sønner av Norge",runtime: 87},{tmdb_id: 57990,poster: "http://image.tmdb.org/t/p/original/izqeD3bwkyR1MAVIc0zu5aeE09L.jpg",imdb_id: "tt0056547",countries: {no: "Norway"},popularity: 0.655,summary: "",originaltitle: "Sønner av Norge kjøper bil",directors: ["Øyvind Vennerød"],release: "1962-01-01",title: "Sønner av Norge kjøper bil",runtime: 98}]};

            // $.getJSON('/json/tmdb/search/?title={0}'.format(title), function(results) {
            $.each(dummy, function(i, results) {
                // Append results
                // $.each(results.films, function(i, production) {
                $.each(results, function(i, production) {
                    // Production
                    var rendered_result = $(result_template(production));
                    var form = rendered_result.find('form[name="submit_production"]');

                    target.append(rendered_result);

                    // Set active (editable) when clicked
                    rendered_result.on('click', function(e) {
                        if (!rendered_result.hasClass('active')) {
                            rendered_result.addClass('active'); 
                            rendered_result.find(':input').prop('disabled', false);
                            rendered_result.find(':input').first().focus();
                        }
                    }).children().find('button').click(function(e) {
                        return false;
                    });
                    
                    // Button events
                    rendered_result.find('button[name="add"]').on('click', function(e) {
                        form.trigger('submit');    
                    });
                    rendered_result.find('button[name="abort"]').on('click', function(e) {
                        // Deactivate (abort)
                        rendered_result.removeClass('active');
                        rendered_result.find(':input').prop('disabled', true);
                    });

                    // Submit
                    form.on('submit', function(e) {
                        e.preventDefault();
                        var search_form = $(this);
                        console.log('submit')
                    });
                });

                // Re-enable inputs
                search_form.find(':input').prop('disabled', false);
            });
        // });
    }
}