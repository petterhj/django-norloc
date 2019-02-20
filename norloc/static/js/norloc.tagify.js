function TagInput(input, template) {
    var controller,
        template = Handlebars.compile(template.html()),
        whitelist = (input.val() ? JSON.parse(input.val()) : []),
        source_url = input.data('source');

    var taginput = new Tagify(input[0], {
        tagTemplate : function(value, data){
            return `<tag title="${value}">
                     <x title="Slett"></x>
                     ${template(data)}
                    </tag>`;
        },
        dropdown : {
            enabled: 3,
            maxItems: 10,
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

    $(taginput.DOM.scope).attr('placeholder', $(input).attr('placeholder'));

    taginput.on('input', function(event) {
        var value = event.detail;
        taginput.settings.whitelist.length = 0;

        controller && controller.abort();
        controller = new AbortController();

        fetch(source_url, {signal: controller.signal})
            .then(RES => RES.json())
            .then(function(whitelist) {
                taginput.settings.whitelist = whitelist.tags;
                taginput.dropdown.show.call(taginput, value); // render the suggestions dropdown
            });
    });

    return taginput;
}