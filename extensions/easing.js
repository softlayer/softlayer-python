/*
#  Easing
#  A smooth, animated page scroller for anchors and predefined classes (requires jQuery Easing plugin)
#
#  Copyright © SoftLayer, an IBM Company
#  Code and documentation licensed under MIT
*/

$("a[href*=#]:not([href=#])").click(function() {
  if (location.pathname.replace(/^\//,"") == this.pathname.replace(/^\//,"") || location.hostname == this.hostname) {
    var target = $(this.hash);
        target = target.length ? target : $("[name=" + this.hash.slice(1) +"]");

    if (target.length) {
      $("html,body").animate({
        scrollTop: target.offset().top
      }, 1000);

      return false;
    }
  }
});
