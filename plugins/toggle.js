/*
#  Toggle
#  Enables sliding/collapsing behavior for navigation
#
#  Copyright © SoftLayer, an IBM Company
#  Code and documentation licensed under MIT
*/

body           = document.body;
iconElement    = document.getElementById("icon-element");
navElement     = document.getElementById("nav-element");
subnavElement  = document.getElementById("subnav-element");
toggleElement  = document.getElementById("toggle-element");

toggleElement.onclick = function() {
    classify.toggle(body, "push");
    classify.toggle(navElement, "pull");
    classify.toggle(iconElement, "hidden");
    classify.toggle(toggleElement, "fixed");
    if (typeof(subnavElement) !== undefined && subnavElement !== null) {
        classify.toggle(subnavElement, "hidden");
    }
};
