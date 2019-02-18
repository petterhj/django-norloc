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

        // Clickable elements
        $('[data-href]').on('click', function() {
            window.location.href = $(this).data('href');
        });

        // Edit mode
        if (getURLParameter('edit') === 'true') {
            $('body').attr('data-edit', true);
        }
    },

    // View: Index
    index: function() {
        // Focus search input
        $('input#search').focus();
    },

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
            return (is_double || shot_count == 1) ? 'double' : '';
        });

        Handlebars.registerHelper('timecode', function(seconds) {
            // return moment.duration(seconds)//.format('HH:mm:SS');
            return moment.utc(seconds * 1000).format('HH:mm:ss');
        });
                
        // Load locations
        var ppk = $('body').data('content-pk');

        UTIL.log('Fetching locations for production {0}'.format(ppk));

        $.getJSON('/json/production/{0}/locations/'.format(ppk), function(locations) {
            $.each(locations, function(i, location) {
                var rendered = $(template(location));
                
                $('section#content').append(rendered.hide().fadeIn('slow'));

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
            $('section#content').append($('div.location.add').show());
        });

        // Edit mode
        if ($('body').data('edit')) {
            // Poster
            $('input[name="poster"]').on('change', function(e) {
                if (this.files && this.files[0]) {
                    var reader = new FileReader();

                    reader.onload = function(e) {
                        $('section#header img.poster').attr('src', e.target.result);
                    }

                    reader.readAsDataURL(this.files[0]);
                }
            });

            // Tags
            TagInput($('input[name="directors"]'), $('#tag-template'), '/json/tags/people');
            TagInput($('input[name="writers"]'), $('#tag-template'), '/json/tags/people');
            TagInput($('input[name="photographers"]'), $('#tag-template'), '/json/tags/people');
            TagInput($('input[name="producers"]'), $('#tag-template'), '/json/tags/companies');
            TagInput($('input[name="distributors"]'), $('#tag-template'), '/json/tags/companies');

            // Process form
            $(document).bind('keydown', 'ctrl+s', function(e) {
                e.preventDefault();
                $('form#production_form').submit();
            }).bind('keydown', 'esc', function(e) {
                e.preventDefault();
                window.location = $('section#caption i.zmdi-close').parent().attr('href');
            });

            $('section#caption i.zmdi-save').on('click', function(e) {
                e.preventDefault();
                $('form#production_form').submit();
            });
        }   
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
        var target = $('section#content');
        var template = Handlebars.compile($('#production-result-template').html());

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
            $.getJSON('/json/tmdb/search/?title={0}'.format(title), function(results) {
                // Append results
                $.each(results.films, function(i, production) {
                    console.log('---------------------------')
                    console.log(production);
                    // Production
                    var rendered = $(template(production));

                    target.append(rendered);

                    // Get details and check if "appliable"
                    $.getJSON('/json/tmdb/details/{0}'.format(production.tmdb_id), function(details) {
                        if (details) {
                            // Add extra metadata
                            if (details.directors.length > 0) {
                                rendered.find('h4').text(details.directors.map(function(elem){
                                    return elem.name;
                                }).join(', '));
                            }
                            if (details.runtime > 0) {
                                rendered.find('.tag.runtime').show()
                                    .find('span').text(details.runtime);
                            }
                            // Check if valid production country
                            if (details.production_countries) {
                                var countries = Object.keys(details.production_countries);

                                rendered.find('.tag.countries').show()
                                    .find('span').text(countries.join(', '));

                                if (countries.includes('NO')) {
                                    rendered.appendTo($('div#focused'));
                                    rendered.removeClass('minified faded');
                                    rendered.find('.add').show().on('click', function() {
                                        // Select film
                                        window.location = '/productions/import/{0}'.format(production.tmdb_id);
                                    });
                                    return;
                                }
                            }
                        }
                    });
                });
                
                // Re-enable inputs
                search_form.find(':input').prop('disabled', false);
            });
        // });
    }
}