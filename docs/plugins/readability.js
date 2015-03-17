/*
#  Readability
#  A polyfill for HTML5 accessibilty and estimator to tell how long it'll take to read a single page
#
#  Copyright © Softlayer, an IBM Company
#  Code and documentation licensed under MIT
*/

ReadifyHTML5 = function(defaults, more_fixes) {

    var fix,
        key,
        mo;

    fixes = {
        article:      { role: "article" },
        aside:        { role: "complementary" },
        nav:          { role: "navigation" },
        main:         { role: "main" },
        section:      { role: "region" },
        output:       { "aria-live": "polite" },
        "[required]": { "aria-required": "true" }
    };

    result = {
        ok:   [],
        warn: [],
        fail: []
    };

    error       = result.fail;
    ATTR_SECURE = new RegExp("aria-[a-z]+|role|tabindex|title|alt|data-[\\w-]+|lang|" + "style|maxlength|placeholder|pattern|required|type|target|accesskey|longdesc");
    ID_PREFIX   = "acfy-id-";
    n_label     = 0;

    docs = document;
    if (docs.querySelectorAll) {
        if (defaults) {
            if (defaults.header) {
                fixes[defaults.header] = {
                    role: "banner"
                };
            }
            if (defaults.footer) {
                fixes[defaults.footer] = {
                    role: "contentinfo"
                };
            }
            if (defaults.main) {
                fixes[defaults.main] = {
                    role: "main"
                };
                fixes.main = {
                    role: ""
                };
            }
        }
        if (more_fixes && more_fixes._CONFIG_ && more_fixes._CONFIG_.ignore_defaults) {
            fixes = more_fixes;
        }
        else {
            for (mo in more_fixes) {
                fixes[mo] = more_fixes[mo];
            }
        }
        for (fix in fixes) {
            if (fix.match(/^_(CONFIG|[A-Z]+)_/)) {
                continue;
            }
            if (fixes.hasOwnProperty(fix)) {
                try {
                    elems = docs.querySelectorAll(fix);
                }
                catch (_error) {
                    ex = _error;
                    error.push({
                        sel:  fix,
                        attr: null,
                        val:  null,
                        msg:  "Invalid syntax for `document.querySelectorAll` function",
                        ex:   ex
                    });
                }
                obj = fixes[fix];
                if (!elems || elems.length < 1) {
                    result.warn.push({
                        sel:  fix,
                        attr: null,
                        val:  null,
                        msg:  "Not found"
                    });
                }
                i = 0;

                while (i < elems.length) {
                    for (key in obj) {
                        if (obj.hasOwnProperty(key)) {
                            attr  = key;
                            value = obj[key];
                            if (attr.match(/_?note/)) {
                                continue;
                            }
                            if (!attr.match(ATTR_SECURE)) {
                                error.push({
                                    sel:  fix,
                                    attr: attr,
                                    val:  null,
                                    msg:  "Attribute not allowed",
                                    re:   ATTR_SECURE
                                });
                                continue;
                            }
                            if (!(typeof value).match(/string|number|boolean/)) {
                                error.push({
                                    sel:  fix,
                                    attr: attr,
                                    val:  value,
                                    msg:  "Value-type not allowed"
                                });
                                continue;
                            }
                            by_match = attr.match(/(describ|label)l?edby/);
                            if (by_match) {
                                try {
                                    el_label = docs.querySelector(value);
                                }
                                catch (_error) {
                                    ex = _error;
                                    error.push({
                                        sel:  fix,
                                        attr: attr,
                                        val:  value,
                                        msg:  "Invalid selector syntax (2) - see 'val'",
                                        ex:   ex
                                    });
                                }
                                if (!el_label) {
                                    error.push({
                                        sel:  fix,
                                        attr: attr,
                                        val:  value,
                                        msg:  "Labelledby ref not found - see 'val'"
                                    });
                                    continue;
                                }
                                if (!el_label.id) {
                                    el_label.id = ID_PREFIX + n_label;
                                }
                                value = el_label.id;
                                attr  = "aria-" + ("label" === by_match[1] ? "labelledby" : "describedby");
                                n_label++;
                            }

                            if (!elems[i].hasAttribute(attr)) {
                                elems[i].setAttribute(attr, value);
                                result.ok.push({
                                    sel:  fix,
                                    attr: attr,
                                    val:  value,
                                    msg:  "Added"
                                });
                            }
                            else {
                                result.warn.push({
                                    sel:  fix,
                                    attr: attr,
                                    val:  value,
                                    msg:  "Already present, skipped"
                                });
                            }
                        }
                    }
                    i++;
                }
            }
        }
    }

    result.input = fixes;
    return result;
};

(function($) {
    $.fn.readEstimate = function(options) {
        if (!this.length) {return this;}

        var plugin   = this;
            el       = $(this);
            defaults = {
                readOutput:         ".estimate",
                wordCount:          null,
                wordsPerMinute:     290, // balance count for words in <pre>/<code> by bumping var up from 270
                roundup:            true,
                lessThanOneMinute:  "",
                prependTime:        "",
                prependWord:        ""
            };

            plugin.settings = $.extend({}, defaults, options);

            var readOutput        = plugin.settings.readOutput;
                wordCount         = plugin.settings.wordCount;
                wordsPerMinute    = plugin.settings.wordsPerMinute;
                roundup           = plugin.settings.roundup;
                lessThanOneMinute = plugin.settings.lessThanOneMinute;
                prependTime       = plugin.settings.prependTime;
                prependWord       = plugin.settings.prependWord;

            if (wordCount < wordsPerMinute) {
                var lessThanOneMinute = lessThanOneMinute || "Less than a min read";
                minuteOutput = "min read";
            }

            var setTime = function(text) {
                var totalWords         = text.trim().split(/\s+/g).length;
                    wordsPerSecond     = wordsPerMinute / 60;
                    totalTimeInSeconds = totalWords / wordsPerSecond;

                if (roundup === true) {
                    readTimeInMinutes = Math.round(totalTimeInSeconds / 60);
                }
                else {
                    Math.floor(totalTimeInSeconds / 60);
                }

                var readTimeInSeconds = Math.round(totalTimeInSeconds - readTimeInMinutes * 60);
                if (roundup === true) {
                    if (readTimeInMinutes > 0) {
                        $(readOutput).text(prependTime + readTimeInMinutes + " " + minuteOutput);
                    }
                    else {
                        $(readOutput).text(prependTime + lessThanOneMinute);
                    }
                }
                else {
                    var readEstimate = readTimeInMinutes + ":" + readTimeInSeconds;
                    $(readOutput).text(prependTime + readEstimate);
                }

                if (wordCount !== "" && wordCount !== undefined) {
                    $(wordCount).text(prependWord + totalWords);
                }
            };

            el.each(function() {
                setTime(el.text());
            }
        );
    };
})(jQuery);
