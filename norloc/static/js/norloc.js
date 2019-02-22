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
            
            UTIL.log('Edit mode enabled for view "{0}"'.format($('body').data('view')));

            // Poster/Headshot
            // $('input[name="poster"],input[name="headshot"]').on('change', function(e) {
            //     if (this.files && this.files[0]) {
            //         var reader = new FileReader();

            //         reader.onload = function(e) {
            //             $('section#header img.poster, section#header img.headshot').attr('src', e.target.result);
            //         }

            //         reader.readAsDataURL(this.files[0]);
            //     }
            // });

            // Tag fields
            if ($('#tag-template').length > 0) {
                $('input.tagify').each(function() {
                    TagInput($(this), $('#tag-template'))
                });
            }

            // Process form
            $(document).bind('keydown', 'ctrl+s', function(e) {
                e.preventDefault();
                $('section#header form').submit();
            }).bind('keydown', 'esc', function(e) {
                e.preventDefault();
                window.location = $('section#caption i.zmdi-close').parent().attr('href');
            });

            $('section#caption i.zmdi-save').on('click', function(e) {
                e.preventDefault();
                $('section#header form').submit();
            });
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
        var form = $('form[name="search"]');
        var target = $('section#content');
        var template = Handlebars.compile($('#production-result-template').html());

        // Search production
        form.on('submit', function(e) {
            e.preventDefault();

            var title = form.find('input[name="query"]').val();

            if (!title) {
                return;
            }

            UTIL.log('Searching for production: {0}'.format(title))

            // Remove any previous results
            target.find('div.production').fadeOut(function() { $(this).remove(); })

            // Temporarily disable inputs
            form.find(':input').prop('disabled', true);

            // Search productions
            $.getJSON('/json/tmdb/production/search/?title={0}'.format(title), function(results) {
                // Append results
                $.each(results.films, function(i, production) {
                    // Production
                    var rendered = $(template(production));

                    target.append(rendered);

                    // Get details and check if "appliable"
                    $.getJSON('/json/tmdb/production/details/{0}'.format(production.tmdb_id), function(details) {
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
                                    rendered.find('.add')
                                        .removeClass('hidden')
                                        .on('click', function() {
                                            // Select film
                                            window.location = '/produksjoner/import/{0}'.format(production.tmdb_id);
                                        });
                                    return;
                                }
                            }
                        }
                    });
                });
                
                // Re-enable inputs
                form.find(':input').prop('disabled', false);
            });
        });
    },

    // View: Import person
    import_person: function() {
        // Template
        var form = $('form[name="search"]');
        var target = $('section#content');
        var template = Handlebars.compile($('#person-result-template').html());

        // Search production
        form.on('submit', function(e) {
            e.preventDefault();

            var name = form.find('input[name="query"]').val();

            if (!name) {
                return;
            }

            UTIL.log('Searching for person: {0}'.format(name))

            // Remove any previous results
            target.find('div.person').fadeOut(function() { $(this).remove(); })

            // Temporarily disable inputs
            form.find(':input').prop('disabled', true);

            // Search productions
            $.getJSON('/json/tmdb/people/search/?name={0}'.format(name), function(results) {
                // Append results
                $.each(results.persons, function(i, person) {
                    // Person
                    var rendered = $(template(person));

                    rendered.find('.add').on('click', function() {
                        // Select person
                        // window.location = '/productions/import/{0}'.format(production.tmdb_id);
                    });

                    if (person.popularity >= 1) {
                        rendered.appendTo($('div#focused'));
                        rendered.removeClass('minified');

                        // Get details
                        $.getJSON('/json/tmdb/people/details/{0}'.format(person.tmdb_id), function(details) {
                            rendered.find('h4').text(details.known_for_department);
                        });
                        return;
                    }

                    rendered.appendTo(target);
                });
                
                // Re-enable inputs
                form.find(':input').prop('disabled', false);
            });
        });
    }
}