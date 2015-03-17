/*
#  Indexing
#  A simple on-page TOC/index generator for h1 headings
#
#  Copyright © SoftLayer, an IBM Company
#  Code and documentation licensed under MIT
*/

(function($) {
    $.fn.indexing = function (options) {
        headings = $("h1").filter(function() {
            return this.id;
        });
        output = $(this);

        if (!headings.length || headings.length < 1 || !output.length) {
            return;
        }

        get_level = function(ele) {
            return parseInt(ele.nodeName.replace("H", ""), 10);
        };

        level = get_level(headings[0]);
        this_level = void 0;
        html = "";

        headings.on("click", function() {
            window.location.hash = this.id;
        })
            .each(function(_, heading) {
            this_level = get_level(heading);

            if (this_level === level) {
                html += "<li><a href='#" + heading.id + "'>" + heading.innerHTML + "</a>";
            }
            level = this_level;
        });

        output.html(html);
    };
})(jQuery);
