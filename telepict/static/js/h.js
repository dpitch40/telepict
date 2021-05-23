function h(tagName, attrs) {
    var children = [];
    for (var _i = 2; _i < arguments.length; _i++) {
        children[_i - 2] = arguments[_i];
    }
    var elem = typeof tagName === 'string' ? document.createElement(tagName) : tagName;
    if (attrs) {
        var style = attrs.style;
        if (attrs.class)
            elem.className = attrs.class;
        delete attrs.style;
        delete attrs.class;
        Object.assign(elem, attrs);
        if (style)
            Object.assign(elem.style, style);
    }
    for (var _a = 0, children_1 = children; _a < children_1.length; _a++) {
        var child = children_1[_a];
        elem.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
    }
    return elem;
}
