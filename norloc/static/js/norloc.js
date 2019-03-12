/*  NORLOC
  ================================================================================== */

// NORLOC
var NORLOC = NORLOC || {
    // Options
    options: {
        name: 'NORLOC',
        debug: true,
        is_authenticated: DJANGO_USER,
    },

    mapdebug: undefined,

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
            console.log('Navigating to {0}'.format($(this).data('href')));
            window.location.href = $(this).data('href');
        });

        // Edit mode
        if (getURLParameter('edit') === 'true') {
            $('section#document').attr('data-edit', true);
            
            UTIL.log('Edit mode enabled for view "{0}"'.format($('#document').data('view')));

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

        // Debug
        if (NORLOC.options.debug) {
            var debug = $('<div>', {'id': 'debug'});
            debug.append($('<span>', {'class': 'mq'}).text('MQ:'));
            debug.append($('<span>', {'class': 'res'}));
            debug.append($('<span>', {'class': 'links'})
                .append('<a href="/produksjoner/import/">Import</a> | ')
                .append('<a href="/produksjoner/film/folk-flest-bor-i-kina/">P1: FFBIK</a> | ')
                .append('<a href="/produksjoner/film/oslo-31-august/">P1: O31A</a> | ')
                .append('<a href="/person/erlend-loe/">F1: EL</a> | ')
                .append('<a href="/produksjoner/film2/">ERROR</a>')
            );
            update_debug();
            function update_debug(e) {
                var w = document.body.clientWidth;
                let h = document.body.clientHeight;
                debug.find('span.res').text(w + ' x ' + h);
            }
            $(window).resize(update_debug);
            $('body').append(debug);
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

        Handlebars.registerHelper('shot_size', function(is_double, shot_count) {
            return (is_double || shot_count == 1) ? 'double' : '';
        });

        Handlebars.registerHelper('timecode', function(seconds) {
            // return moment.duration(seconds)//.format('HH:mm:SS');
            return moment.utc(seconds * 1000).format('HH:mm:ss');
        });
                
        // Load locations
        var ppk = $('#document').data('content-pk');

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
            // $('section#content').append($('div.location.add').show());

            // References
            $('section#content').append($('div#references').show());
        });
    },

    // View: Location
    location: function() {
        // Template
        var source   = $('#production-template').html();
        var template = Handlebars.compile(source);

        Handlebars.registerHelper('shot_size', function(is_double, shot_count) {
            return (is_double || shot_count == 1) ? 'double' : '';
        });

        Handlebars.registerHelper('timecode', function(seconds) {
            // return moment.duration(seconds)//.format('HH:mm:SS');
            return moment.utc(seconds * 1000).format('HH:mm:ss');
        });

        // Load productions
        var lpk = $('#document').data('content-pk');

        UTIL.log('Fetching productions for location {0}'.format(lpk));

        $.getJSON('/json/location/{0}/productions/'.format(lpk), function(productions) {
            $.each(productions, function(ppk, production) {
                var rendered = $(template(production));
                
                $('section#content').append(rendered.hide().fadeIn('slow'));
            });

            // References
            $('section#content').append($('div#references').show());
        });
    },

    // View: Map
    map: function() {
        // Map
        var map = new L.Map.NorlocMap('map', {
            center: [59.927669, 10.741541],
            zoom: 15,
        });
        
        // Locations
        $.getJSON('/json/locations/?bounds=true', function(result) {
            $.each(result.locations, function(i, location) {
                // Create location polygon
                if (location.bounds.length > 3) {
                    new L.Polygon.LocationPolygon(location.bounds, {
                        locationId: location.pk,
                        locationAddress: location.full_address,
                    }).addTo(map.featureGroups.locations);
                }
            });

            // Scenes
            $.getJSON('/json/scenes/', function(scenes) {
                $.each(scenes, function(spk, scene) {
                    // Shots
                    var shots_coordinates = [];

                    $.each(scene.shots, function(shpk, shot) {
                        if (shot.coordinate) {
                            // Coordinate
                            shots_coordinates.push(shot.coordinate);

                            // Marker
                            var marker = new L.Marker.ShotMarker(shot.coordinate, {
                                shotId: shpk,
                                production: scene.production,
                                icon: L.divIcon({
                                    className: 'mapShotMarker',
                                    html: '<img src="{0}">'.format((shot.image ? shot.image : '/static/img/bullet_blue.png'))
                                })
                            }).addTo(map.featureGroups.shots);
                        }
                    });

                    // Connect shots in same scene
                    if (shots_coordinates.length > 1) {
                        L.polyline(shots_coordinates, {
                            color: '#345C7C',
                            opacity: 0.3,
                            weight: 3,
                            dashArray: '1 4',
                        }).addTo(map.featureGroups.shots);
                    }
                });

                // Fit bounds
                // map.fitBounds(map.featureGroups.locations.getBounds());

                ////////////////////
                // map.toggleEditMode();
                ////////////////////
            });
        });

        $('section#caption a.right > i.zmdi').on('click', function(e) {
            e.preventDefault();

            if ($(this).hasClass('zmdi-edit')) {
                window.history.replaceState(null, null, '?edit=true');
                $(this).removeClass('zmdi-edit').addClass('zmdi-close');
            } else {
                window.history.replaceState(null, null, window.location.pathname);
                $(this).removeClass('zmdi-close').addClass('zmdi-edit');
            }
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
                console.log(results);
                
                $.each(results.productions, function(i, production) {
                    console.log(production);
                    console.log('-------------------')
                    // Production
                    var rendered = $(template(production));

                    target.append(rendered);

                    // Get details and check if "appliable"
                    $.getJSON('/json/tmdb/production/{0}/details/{1}'.format(production.type, production.tmdb_id), function(details) {
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
                                var countries = details.production_countries;

                                rendered.find('.tag.countries').show()
                                    .find('span').text(countries.join(', '));

                                if (countries.includes('NO')) {
                                    rendered.appendTo($('div#focused'));
                                    rendered.removeClass('minified faded');
                                    rendered.find('.add')
                                        .removeClass('hidden')
                                        .on('click', function() {
                                            // Select film
                                            window.location = '/produksjoner/import/{0}/{1}'.format(production.type, production.tmdb_id);
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