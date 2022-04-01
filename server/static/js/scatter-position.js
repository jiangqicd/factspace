!function () {
    "use strict";
    var t = "undefined" == typeof global ? self : global;
    if ("function" != typeof t.require) {
        var e = {}, i = {}, n = {}, r = {}.hasOwnProperty, s = /^\.\.?(\/|$)/, o = function (t, e) {
            for (var i, n = [], r = (s.test(e) ? t + "/" + e : e).split("/"), o = 0, h = r.length; o < h; o++) i = r[o], ".." === i ? n.pop() : "." !== i && "" !== i && n.push(i);
            return n.join("/")
        }, h = function (t) {
            return t.split("/").slice(0, -1).join("/")
        }, u = function (e) {
            return function (i) {
                var n = o(h(e), i);
                return t.require(n, e)
            }
        }, c = function (t, e) {
            var n = x && x.createHot(t), r = {id: t, exports: {}, hot: n};
            return i[t] = r, e(r.exports, u(t), r), r.exports
        }, l = function (t) {
            return n[t] ? l(n[t]) : t
        }, f = function (t, e) {
            return l(o(h(t), e))
        }, a = function (t, n) {
            null == n && (n = "/");
            var s = l(t);
            if (r.call(i, s)) return i[s].exports;
            if (r.call(e, s)) return c(s, e[s]);
            throw new Error("Cannot find module '" + t + "' from '" + n + "'")
        };
        a.alias = function (t, e) {
            n[e] = t
        };
        var d = /\.[^.\/]+$/, p = /\/index(\.[^\/]+)?$/, w = function (t) {
            if (d.test(t)) {
                var e = t.replace(d, "");
                r.call(n, e) && n[e].replace(d, "") !== e + "/index" || (n[e] = t)
            }
            if (p.test(t)) {
                var i = t.replace(p, "");
                r.call(n, i) || (n[i] = t)
            }
        };
        a.register = a.define = function (t, n) {
            if (t && "object" == typeof t) for (var s in t) r.call(t, s) && a.register(s, t[s]); else e[t] = n, delete i[t], w(t)
        }, a.list = function () {
            var t = [];
            for (var i in e) r.call(e, i) && t.push(i);
            return t
        };
        var x = t._hmr && new t._hmr(f, a, e, i);
        a._cache = i, a.hmr = x && x.wrap, a.brunch = !0, t.require = a
    }
}(), function () {
    "undefined" == typeof window ? this : window;
    require.register("lib.js", function (t, e, i) {
        "use strict";

        function n(t, e) {
            if (!(t instanceof e)) throw new TypeError("Cannot call a class as a function")
        }

        var r = function () {
            function t(t, e) {
                for (var i = 0; i < e.length; i++) {
                    var n = e[i];
                    n.enumerable = n.enumerable || !1, n.configurable = !0, "value" in n && (n.writable = !0), Object.defineProperty(t, n.key, n)
                }
            }

            return function (e, i, n) {
                return i && t(e.prototype, i), n && t(e, n), e
            }
        }(), s = e("seedrandom"), o = function f(t, e) {
            n(this, f), this.x = t, this.y = e
        }, h = function a(t, e) {
            n(this, a), this.width = t, this.height = e
        }, u = function d(t, e, i, r) {
            n(this, d), this.start = new o(t, e), this.end = new o(i, r)
        }, c = function () {
            function t(e, i, r, s, u) {
                n(this, t), this.position = new o(e, i), this.size = new h(r, s), this.fromCenter = void 0 == u
            }

            return r(t, [{
                key: "overlaps", value: function (t, e) {
                    var i = this.position, n = t.position, r = this.size, s = t.size;
                    if (this.fromCenter) {
                        if (i.x >= n.x - r.width / 2 - s.width / 2 - e && i.x <= n.x + r.width / 2 + s.width / 2 + e && i.y >= n.y - r.height / 2 - s.height / 2 - e && i.y <= n.y + r.height / 2 + s.height / 2 + e) return !0
                    } else if (i.x + r.width + e >= n.x && i.x <= n.x + s.width + e && i.y + r.height + e >= n.y && i.y <= n.y + s.height + e) return !0;
                    return !1
                }
            }]), t
        }(), l = function () {
            function t() {
                n(this, t), this.blocks = [], this.fromCenter = !0, this.size = new h(10, 10), this.between = new h(100, 100), this.exclude = !1, this.gutter = 0
            }

            return r(t, [{
                key: "fromTopLeft", value: function () {
                    return this.fromCenter = !1, this
                }
            }, {
                key: "withBounds", value: function (t, e) {
                    return this.between = new h(t, e), this
                }
            }, {
                key: "ofSize", value: function (t, e) {
                    return this.size = new h(t, e), this
                }
            }, {
                key: "withGutter", value: function (t) {
                    return this.gutter = t, this
                }
            }, {
                key: "withExclude", value: function (t, e, i, n) {
                    return this.exclude = new u(t, e, i, n), this
                }
            }, {
                key: "valid", value: function (t) {
                    for (var e = 0; e < this.blocks.length; e++) {
                        var i = this.blocks[e];
                        if (t.overlaps(i, this.gutter)) return !1
                    }
                    return this.fromCenter ? this.exclude === !1 || !(t.position.x + t.size.width / 2 >= this.exclude.start.x && t.position.x - t.size.width / 2 <= this.exclude.end.x && t.position.y + t.size.height / 2 >= this.exclude.start.y && t.position.y - t.size.height / 2 <= this.exclude.end.y) : this.exclude === !1 || !(t.position.x + t.size.width >= this.exclude.start.x && t.position.x <= this.exclude.end.x && t.position.y + t.size.height >= this.exclude.start.y && t.position.y <= this.exclude.end.y)
                }
            }, {
                key: "generate", value: function (t) {
                    this.blocks = [];
                    for (var e = 0; e < t; e++) {
                        var i = void 0;
                        do i = new c(s()() * this.between.width, s()() * this.between.height, this.size.width, this.size.height, this.fromCenter); while (!this.valid(i));
                        this.blocks.push(i)
                    }
                    return this.blocks
                }
            }]), t
        }();
        i.exports.Pos = o, i.exports.Bounds = h, i.exports.Zone = u, i.exports.Block = c, i.exports.Positions = l
    }), require.register("___globals___", function (t, e, i) {
    })
}(), require("___globals___");
