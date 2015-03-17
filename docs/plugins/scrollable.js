/*
#  Scrollable
#  Thresholds and smooth animations for page scrolling
#
#  Copyright © SoftLayer, an IBM Company
#  Code and documentation licensed under MIT
*/


pageOffset = document.documentElement.scrollTop || document.body.scrollTop;
scrollTo = function(element, to, duration) {
    start         = element.scrollTop;
    change        = to - start;
    currentTime   = 0;
    increment     = 20;

    animateScroll = function() {
        currentTime += increment;
        val = Math.easeInOutQuad(currentTime, start, change, duration);
        element.scrollTop = val;
        if (currentTime < duration) {
            setTimeout(animateScroll, increment);
        }
    };

    Math.easeInOutQuad = function(t, b, c, d) { t /= d / 2;
        if (t < 1) { return c / 2 * t * t + b; }
        t--; return -c / 2 * (t * (t - 2) - 1) + b; };

    animateScroll();
};

window.onscroll = function() {
    if (pageYOffset >= 200) {
        document.getElementById("top").style.visibility = "visible";
    }
    else {
        document.getElementById("top").style.visibility = "hidden";
        return;
    }
    document.getElementById("top").onclick = function() {
        scrollTo(document.body, 0, 0);
    };
};

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
