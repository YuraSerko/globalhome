var wrap = function(obj, funcname) {
        var func = function() {
            obj[funcname]();
        }
        return func;
    }

var Node = function(domElement, tree) {
    this.tree = tree;
    this.is_open = false;
    this.is_visible = false;
    this.hasChildren = false;

    this.init = function(domElement) {
        this.level = 0;
        this.node = $(domElement);
		this.icon = this.node.find('.icon');
        var result = /^node((\d+)-)?(\d+)$/i.exec(this.node.attr('id'));
        if (result) {
            if (result[2]) {
                this.parent_id = parseInt(result[2]);
            }
            this.id = parseInt(result[3]);
        }
        this.tr = this.node.parent().parent();
        this.is_visible = this.tr.css('display') == 'none' ? false : true;
    }

    this.init(domElement);

    this.addParent = function(parent) {
        this.parent = parent;
        this.level = parent.level + 1;
        parent.hasChildren = true;
    }

    this.toggle = function() {
        if (this.is_open) {
            this.close();
        }
        else {
            this.open();
        }
    }

    this.icon.bind('click', wrap(this, 'toggle'));

    this.open = function() {
        if (!this.hasChildren) return;
        if (!this.is_visible) this.show();
        var children = this.getChildren();
        for (var i=0; i<children.length; i++) {
            children[i].show();
        }
        this.is_open = true;
        this.icon.removeClass('closed');
        this.icon.addClass('open');
        this.tree.save();
        this.tree.colorizeRows();
    }

    this.close = function() {
        if (!this.hasChildren) return;
        var children = this.getChildren();
        for (var i=0; i<children.length; i++) {
            children[i].hide();
        }
        this.is_open = false;
        this.icon.removeClass('open');
        this.icon.addClass('closed');
        this.tree.save();
        this.tree.colorizeRows();
    }

    this.show = function(){
        this.tr.show();
        this.is_visible = true;
    }

    this.hide = function(){
        this.close();
        this.tr.hide();
        this.is_visible = false;
    }

    this.getChildren = function(){
        return this.tree.getChildren(this);
    }
}

var Tree = function(config) {
    this.nodes = [];
    this.config = config ? config : {};
    this.in_work = false;
    this.init = function() {
        var elems = $('.tree-node');
        for (var i=0; i<elems.length; i++) {
            var node = new Node(elems[i], this);
            var parent = this.getParent(node);
            if (parent) {
                node.addParent(parent);
            }
            var children = this.getChildren(node);
            if (children.length > 0) {
                for (var i=0; i<children.length; i++) {
                    children[i].addParent(node);
                }
            }
            this.nodes.push(node);
        }
    }

    this.getParent = function(node) {
        for (var i=0; i<this.nodes.length; i++) {
            if (this.nodes[i].id == node.parent_id) {
                return this.nodes[i];
            }
        }
        return null;
    }

    this.setState = function() {
        this.in_work = true;
        var state = $.cookie('tree-state');
        state = state ? $.evalJSON(state) : [];
        for (var i=0; i<this.nodes.length; i++) {
            var node = this.nodes[i];
            if (node.hasChildren) {
                node.icon.addClass(node.is_open ? 'open' : 'closed');
            }
            if (!node.parent_id) {
                    node.show();
            }
            if (state.length > 0) {
                for (var j=0; j<state.length; j++) {
                    if (state[j][0] == node.id && state[j][1] == true) {
                        node.open();
                    }
                }
            }
            else {
                if ((typeof this.config['initialOpenLevel'] != undefined) && node.level <= this.config['initialOpenLevel']) {
                    node.open();
                }
            }
        }
        this.in_work = false;
        this.colorizeRows();
    }

    this.colorizeRows = function() {
        if (this.in_work) return;
        var counter = 3;
        for (var i=0; i<this.nodes.length; i++) {
            if (!this.nodes[i].is_visible) {
                continue;
            }
            var classname = 'row' + (counter % 2 ? 1 : 2);
            counter ++;
            this.nodes[i].tr.removeClass('row1');
            this.nodes[i].tr.removeClass('row2');
            this.nodes[i].tr.addClass(classname);
        }
    }

    this.getChildren = function(parent) {
        var nodes = [];
        for(var i=0; i<this.nodes.length; i++){
            if(this.nodes[i].parent_id == parent.id) {
                nodes.push(this.nodes[i]);
                }
            }
        return nodes;
    }

    this.getState = function() {
        var state = [];
        for (var i=0; i<this.nodes.length; i++) {
            var node = this.nodes[i];
            if (node.hasChildren) {
                state.push([node.id, node.is_open]);
            }
        }
        return state;
    }

    this.getStateJSON = function() {
        return $.toJSON(this.getState());
    }

    this.save = function() {
        $.cookie('tree-state', this.getStateJSON());
    }

    this.init();
    this.setState();
}

