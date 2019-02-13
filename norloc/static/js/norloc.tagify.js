function TagInput(input, template, source_url) {
    var controller,
        template = Handlebars.compile(template.html()),
        whitelist = (input.val() ? JSON.parse(input.val()) : []);

    var taginput = new Tagify(input[0], {
        tagTemplate : function(value, data){
            return `<tag title="${value}">
                     <x title="Slett"></x>
                     ${template(data)}
                    </tag>`;
        },
        dropdown : {
            itemTemplate : function(data){
                return `<div class="tagify__dropdown__item">
                         ${template(data)}
                        </div>`
            }
        },
        whitelist: whitelist,
        enforceWhitelist: true,
        keepInvalidTags: false,
        maxTags: 10,
        addTagOnBlur: true
    });

    var label = $('label[for="{0}"]'.format(input.attr('name')));

    if (label.length >  0) {
        $(taginput.DOM.scope).prepend(label);
    }

    taginput.on('input', function(event) {
        var value = event.detail;
        taginput.settings.whitelist.length = 0;

        controller && controller.abort();
        controller = new AbortController();

        fetch(source_url, {signal: controller.signal})
            .then(RES => RES.json())
            .then(function(whitelist) {
                taginput.settings.whitelist = whitelist.people;
                taginput.dropdown.show.call(taginput, value); // render the suggestions dropdown
            });
    });

    return taginput;
}