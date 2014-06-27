/*
#  Read
#  Estimates how long it'll take to read a single page
#
#  Copyright © Softlayer, an IBM Company
#  Code and documentation licensed under MIT
*/

(function ($) {
  $.fn.readEstimate = function (options) {
    if (!this.length) {return this;}

    var plugin   = this;
        el       = $(this);
        defaults = {
          readOutput:         ".estimate",
          wordCount:          null,
          wordsPerMinute:     275,
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

    var setTime = function (text) {
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

      el.each(function () {
        setTime(el.text());
      }
    );
  };
})(jQuery);
