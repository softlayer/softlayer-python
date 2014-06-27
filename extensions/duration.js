/*
#  Duration
#  Estimates how long it'll take to read a single page
#
#  Copyright © Softlayer, an IBM Company
#  Code and documentation licensed under MIT
*/

(function ($) {
  $.fn.estimatedTime = function (options) {
    if (!this.length) {return this;}

    var plugin   = this;
        el       = $(this);
        defaults = {
          estimateOutput:    ".duration",
          wordCount:         null,
          wordsPerMinute:    270,
          rounding:          true,
          lessThanOneMinute: "",
          prependTime:       "",
          prependWord:       "",
          remotePath:        null,
          remoteTarget:      null
    };

    plugin.settings = $.extend({}, defaults, options);

    var estimateOutput    = plugin.settings.estimateOutput;
        wordCount         = plugin.settings.wordCount;
        wordsPerMinute    = plugin.settings.wordsPerMinute;
        rounding          = plugin.settings.rounding;
        lessThanOneMinute = plugin.settings.lessThanOneMinute;
        prependTime       = plugin.settings.prependTime;
        prependWord       = plugin.settings.prependWord;
        remotePath        = plugin.settings.remotePath;
        remoteTarget      = plugin.settings.remoteTarget;


    if (wordCount < wordsPerMinute) {
      var lessThanOneMinute = lessThanOneMinute || "Less than a minute";
      minShortForm = "minutes";
    }

    var setTime = function (text) {
      var totalWords = text.trim().split(/\s+/g).length;
      wordsPerSecond = wordsPerMinute / 60;
      totalTimeInSeconds = totalWords / wordsPerSecond;
      if (rounding === true) {
        estimatedTimeInMinutes = Math.round(totalTimeInSeconds / 60);
      }
      else {
        Math.floor(totalTimeInSeconds / 60);
      }

      var estimatedTimeInSeconds = Math.round(totalTimeInSeconds - estimatedTimeInMinutes * 60);
      if (rounding === true) {
        if (estimatedTimeInMinutes > 0) {
          $(estimateOutput).text(prependTime + estimatedTimeInMinutes + " " + minShortForm);
        }
        else {
          $(estimateOutput).text(prependTime + lessThanOneMinute);
        }
      }
      else {
        var estimatedTime = estimatedTimeInMinutes + ":" + estimatedTimeInSeconds;
        $(estimateOutput).text(prependTime + estimatedTime);
      }

      if (wordCount !== "" && wordCount !== undefined) {
        $(wordCount).text(prependWord + totalWords);
      }
    };

    el.each(function () {
      if (remotePath !== null && remoteTarget !== null) {
        $.get(remotePath, function (data) {
          setTime($("<div>").html(data).find(remoteTarget).text());
        });
      }
      else {
        setTime(el.text());
      }
    });
  };
})(jQuery);
