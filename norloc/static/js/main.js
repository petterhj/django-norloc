// String format
if (!String.prototype.format) {
    String.prototype.format = function() {
        var args = arguments;
        return this.replace(/{(\d+)}/g, function(match, number) { 
            return typeof args[number] != 'undefined' ? args[number] : match;
        });
    };
}


// Get URL parameter
function getURLParameter(param) {
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    
    for (var i = 0; i < sURLVariables.length; i++) {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == param) {
            return sParameterName[1];
        }
    }
}


// Get cookcie
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


// Handlebars: Join
Handlebars.registerHelper('join', function(items, block) {
    var delimiter = block.hash.delimiter || ",", 
        start = start = block.hash.start || 0, 
        len = items ? items.length : 0,
        end = block.hash.end || len,
        out = "";

        if(end > len) end = len;

    if ('function' === typeof block) {
        for (i = start; i < end; i++) {
            if (i > start) 
                out += delimiter;
            if('string' === typeof items[i])
                out += items[i];
            else
                out += block(items[i]);
        }
        return out;
    } else { 
        return [].concat(items).slice(start, end).join(delimiter);
    }
});

Handlebars.registerHelper('split', function(string, block) {
    if (!string) { return ''; }
    
    var separator = block.hash.separator || ",";
    var index = block.hash.index || 0;

    return string.split(separator)[index];
});


/*  Utilities
  ================================================================================== */

UTIL = {
    site: NORLOC,
    
    // Execute
    exec: function(view) {
        var ns = this.site;
        var view = (view === undefined) ? 'common' : view;

        if (view && typeof ns[view] == 'function') {
            this.log('View:' + view);
            ns[view]();
        }
    },
 
    // Start
    start: function() {
        // var body = document.body,
        var body = document.getElementById('document'),
            view = body.getAttribute('data-view')
        
        UTIL.exec('common');
        UTIL.exec(view);
    },

    // Get cookie
    getCookie: function(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },
    
    // Log
    log: function(message) {
        if (this.site.options.debug) {
            console.log('[' + this.site.options.name + '] ' + message);
        }
    }
};


/*  Initialize
  ================================================================================== */

$(document).ready(UTIL.start);

