/**
 * Copyright (c) 2009, Nathan Bubna
 * Dual licensed under the MIT and GPL licenses:
 *   http://www.opensource.org/licenses/mit-license.php
 *   http://www.gnu.org/licenses/gpl.html
 *
 * Yet another input text hinting plugin, because the others don't have the
 * flexibility, features and ease i want.  Sigh.  This is the kitchen sink
 * version.  By default it does the "labelOver" thing, but you can set it to 
 * {method:'valueSwap'} if you want to do the more typical value-swapping. It assumes
 * you have a "hint" css class to make your hints visually distinct.  If you know
 * exactly how you'll be using all your inputs and textareas and how you want to
 * do your hints, then use Remy Sharp's or EZPZ-Hint or something.
 * If you want easy options or custom stuff this one should do you well.
 * Here's the basics:
 *
 *  $.hint() turns all possible hints on, using labels or title attributes as the text.
 *  $.hint('[enter value]') turns all possible hints on, using the specified text instead.
 *  $.hint({on:'blur'}) does the above, using 'blur' instead of 'hint' as the class indicating the hint is on.
 *  $.hint({attr:'title'}) forces the hint text to come from the "title" attribute on the element.
 *  $.hint('[enter value]', {on:'blur', method:'valueSwap'}) i think you can extrapolate what this does.
 *  $('.hintme').hint() accepts all the same params and works the same as any and all of
 *                      the above, only limited to the selected portion of the document.
 *
 * Pretty much everything involved in doing this is configurable per call,
 * per field and/or per document.  You can override any function, the css used
 * for doing label-over, the selector used to identify hint-able elements, and
 * so on.  You change things globally by setting them like:
 *
 *  $.hint.query = 'input:text'; //or
 *  $.extend($.hint, { on: 'foo', attr: 'title' });
 *
 * Or locally by passing them in as options (see earlier above).  Yes, that goes
 * for the functions too.
 *
 * If you don't like either the labelOver or valueSwap methods, you can also
 * cleanly and easily plug in your own.  Just structure its functions in an object
 * like the two existing methods.
 *
 * One thing "missing" from this plugin is dimension detection to better automate 
 * position of labels over fields.  So, if your css for your inputs or textareas
 * alter their "box" (borders or margins, especially), then the default positioning
 * of labelOver will need adjustment (via the labelCss option). If anyone would care
 * to contribute better detection/positioning, that'd be swell.
 *
 * Also, if you are using labelOver (the default!) and your input fields are
 * NOT contained inside block-level elements, but instead are "on the same line":
 *
 *  <input type="text">&nbsp;<input type="text">&nbsp; ... etc ...
 *
 * Then you must specify that with the 'inline' property:
 *
 *  $.hint({inline: true}); // or <input class="{inline:true}" ...
 *
 * Otherwise the container divs will force the input elements to be
 * displayed as blocks, breaking your layout.  Which would be sad. :(
 *
 * If you are using the (default) labelOver method and would like to keep the hints
 * visible until the user actually begins entering a value, then you can set the
 * 'toggleOnFocus' option to false:
 *
 *  $('.hintable').hint({toggleOnFocus:false, attr:'title'});
 *
 * NOTE: The toggleOnFocus option is ignored by the valueSwap method, as trying
 * to implement that is likely to accelerate my hair loss.
 *
 * Last, options may be specified in-element if the metadata plugin
 * is available:
 *
 *  <input class="{attr:'name',labelCss:{top:0}}" name="foo" type="text">
 *
 * @version 1.7
 * @name hint
 * @author Nathan Bubna
 */
;(function($) {

    var H = $.hint = function(txt, opts) {
        return $(document).hint(txt, opts);
    },
    toOpts = function(t, o) {
        if (!o && typeof t == "object") { o = t; t = null; }
        o = o || {};
        if (t) { o.text = ''+t; }
        if (o.keepLabel) o.method = 'valueSwap';
        return o;
    };

    $.fn.hint = function(txt, opts) {
        opts = toOpts(txt, opts);
        return this.each(function() {
            H.init.call(this, opts);
        });
    };

    $.extend(H, {
        // properties
        version: "1.7",
        query: 'input:password,input:text:not(._hintPw),textarea',
        on: 'hint',
        toggleOnFocus: true,
        attr: false,
        inline: false,
        text: undefined,
        method: 'labelOver',
        parentCss: { position: 'relative',  float: 'left',  clear: 'left' },
        inlineCss: { display:  'inline',    float: 'none' },
        labelCss:  { position: 'absolute',  top:   '4px',   left:  '5px'  },

        // "static" functions
        getElements: function(opts) {
            var q = opts.query || H.query,
                inputs = this.is(q) ? this : this.find(q);
            return (inputs.length == 0 ? this : inputs);
        },
        init: function(opts) {
            // gather options and elements
            var $e = $(this), meta = $.metadata,
                Hm = meta ? $e.metadata() : null;
            H.getElements.call($e, opts).each(function() {
                var $i = $(this), hm = meta ? $i.metadata() : null,
                    h = $.extend(true, {}, H, Hm, hm, opts);
                $.extend(h, h[h.method]); // shift chosen impl methods into main options
                h.create.call($i, h);
            });
        },

        // "instance" functions
        hasValue: function(h) {
            var v = this.val();
            return (v && $.trim(v) != '');
        },
        start: function() {
            var i = $(this), h = i.data('hint'),
                method = h.hasValue.call(i, h) ? 'hide' : 'show';
            h[method].call(i, h);
        },
        end: function() {
            var i = $(this), h = i.data('hint');
            if (h && h.hasHint.call(i, h)) {
                h.hide.call(i, h);
            }
        },
        getText: function(h) {
            return h.text || this.attr(h.attr || 'title');
        },
        create: function(h) {
            // undo prior hints
            if (this.data('hint')) this.data('hint').destroy.call(this);
            this.data('hint', h);
            h.setup.call(this, h);
            h.start.call(this);
        },
        destroy: function() {
            var h = this.data('hint');
            h.teardown.call(this, h);
            this.data('hint', null);
        },
        valueSwap: {
            setup: function(h) {
                var self = this, text = h.getText.call(self, h);
                h.kill = function() { h.destroy.call(self); };
                if (self.is(':password')) {
                    h.password = $('<input type="text" value="'+text+'" class="_hintPw">').focus(function() {
                        self.show().focus();
                    }).addClass(h.on).insertBefore(self);
                // fix IE value caching on refresh
                } else if ($.browser.msie && !self.attr('defaultValue') && self.val() == text) {
                    self.val('');
                }
                // event bindings...
                self.blur(h.start).focus(h.end);
                $(window).unload(h.kill);
                $(this[0].form).submit(h.kill);
            },
            hide: function(h) {
                if (h.password) {
                    h.password.hide();
                    this.show();
                } else {
                    if (h.hasHint.call(this, h)) this.val('');
                    this.removeClass(h.on);
                }
            },
            show: function(h) {
                if (h.password) {
                    this.hide();
                    h.password.show();
                } else {
                    this.addClass(h.on).val(h.getText.call(this, h));
                }
            },
            hasHint: function(h) {
                if (h.password) return h.password.is(':visible');
                return this.hasClass(h.on) && (this.val() == h.getText.call(this, h));
            },
            teardown: function(h) {
                h.end.call(this);
                if (h.password) h.password.remove();
                $(window).unbind('unload', h.kill);
                $(this[0].form).unbind('submit', h.kill);
            }
        },
        labelOver: {
            setup: function(h) {
                var self = this, n = this.attr('name'),
                    l = $('label[for='+n+']'), p = self.parent();
                if (l.size() == 0) {
                    h.newLabel = true;
                    l = $('<label for="'+n+'">'+h.getText.call(this, h)+'</label>');
                    self.before(l);
                } else if (h.text || h.attr) {
                    h.labelText = l.text();
                    l.text(h.getText.call(this, h));
                }
                p = self.wrap('<div></div>').before(l.remove()).parent().css(h.parentCss);
                if (h.inline) p.css(h.inlineCss);
                h.labelStyle = l.attr('style') || '';
                h.label = l.addClass(h.on).css(h.labelCss).click(function() {
                    self.focus();
                });
                // event bindings...
                if (h.toggleOnFocus) {
                    self.blur(h.start).focus(h.end);
                } else {// toggle on value instead
                    self.keyup(h.toggle = function() {
                        (h.hasValue.call(self, h) ? h.end : h.start).call(self);
                    });
                }
            },
            hide: function(h) {
                h.label.css('textIndent', -10000);
            },
            show: function(h) {
                h.label.css('textIndent', 0);
            },
            hasHint: function(h) {
                return h.label.css('textIndent').charAt(0) == '0';
            },
            teardown: function(h) {
                if (h.toggleOnFocus) {
                    this.unbind('blur', h.start).unbind('focus', h.end);
                } else {
                    this.unbind('keyup', h.toggle);
                }
                h.label.removeClass(h.on).attr('style', h.labelStyle);
                if (h.newLabel) {
                    h.label.remove();
                    h.label = null;
                } else if (h.labelText) {
                    h.label.text(h.labelText);
                }
                var p = this.parent().after(this);
                if (h.label) {
                    p.before(h.label);
                }
                p.remove();
            }
        }
    });

})(jQuery);