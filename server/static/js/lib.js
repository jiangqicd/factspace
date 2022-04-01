const seedrandom = require('seedrandom');

/**
 * Class for an x and y position
 */
class Pos {
    constructor(x, y) {
        this.x = x;
        this.y = y;
    }
}

/**
 * Class for a width and height bounds
 */
class Bounds {
    constructor(w, h) {
        this.width = w;
        this.height = h;
    }
}

/**
 * Class for a set out x and y zone
 */
class Zone {
    constructor(x1, y1, x2, y2) {
        this.start = new Pos(x1, y1);
        this.end = new Pos(x2, y2);
    }
}

/**
 * Class for a block
 */
class Block {
    constructor(x, y, width, height, fromCenter) {
        this.position = new Pos(x, y);
        this.size = new Bounds(width, height);
        this.fromCenter = fromCenter==undefined ? true : fromCenter;
    }

    /**
     * Checks whether a block overlaps
     *
     * @param Block block
     * @param Number gutter
     */
    overlaps(block, gutter) {
        const pos1 = this.position;
        const pos2 = block.position;
        const size1 = this.size;
        const size2 = block.size;
        gutter = gutter==undefined ? 0 : gutter;
        if(this.fromCenter) {
            if(pos1.x>pos2.x-(size1.width/2)-(size2.width/2)-gutter &&
                pos1.x<pos2.x+(size1.width/2)+(size2.width/2)+gutter &&
                pos1.y>pos2.y-(size1.height/2)-(size2.height/2)-gutter &&
                pos1.y<pos2.y+(size1.height/2)+(size2.height/2)+gutter) {
                return true;
            }
        } else {
            if(pos1.x+size1.width+gutter>pos2.x &&
                pos1.x<pos2.x+size2.width+gutter &&
                pos1.y+size1.height+gutter>pos2.y &&
                pos1.y<pos2.y+size2.height+gutter) {
                return true;
            }
        }
        return false;
    }
}

/**
 *
 */
class Positions {
    constructor() {
        this.blocks = [];
        this.fromCenter = true;
        this.size = new Bounds(10, 10);
        this.between = new Bounds(100, 100);
        this.exclude = false;
        this.gutter = 0;
    }

    /**
     * Sets to top left positioning
     * @return Positions
     */
    fromTopLeft() {
        this.fromCenter = false;
        return this;
    }

    /**
     * Sets bounds to generate in
     *
     * @param Number width
     * @param Number height
     * @return Positions
     */
    withBounds(width, height) {
        this.between = new Bounds(width, height);
        return this;
    }

    /**
     * Sets the block size
     *
     * @param Number width
     * @param Number height
     * @return Positions
     */
    ofSize(width, height) {
        this.size = new Bounds(width, height);
        return this;
    }

    /**
     * Sets the gutter size
     *
     * @param Number gutt
     * @return Positions
     */
    withGutter(gutt) {
        this.gutter = gutt;
        return this;
    }

    /**
     * Adds an exclusion zone
     *
     * @param Number x1
     * @param Number y1
     * @param Number x2
     * @param Number y2
     * @return Positions
     */
    withExclude(x1, y1, x2, y2) {
        this.exclude = new Zone(x1, y1, x2, y2);
        return this;
    }

    /**
     * Checks whether positions were taken
     *
     * @param Pos pos
     */
    valid(block) {
        for(let i = 0; i < this.blocks.length; i++) {
            const b = this.blocks[i];
            if(block.overlaps(b, this.gutter)) {
                return false;
            }
        }
        if(this.fromCenter) {
            return (this.exclude===false)||
                (!(block.position.x+block.size.width/2>this.exclude.start.x &&
                    block.position.x-block.size.width/2<this.exclude.end.x &&
                    block.position.y+block.size.height/2>this.exclude.start.y &&
                    block.position.y-block.size.height/2<this.exclude.end.y));
        } else {
            return (this.exclude===false)||
                (!(block.position.x+block.size.width>this.exclude.start.x &&
                    block.position.x<this.exclude.end.x &&
                    block.position.y+block.size.height>this.exclude.start.y &&
                    block.position.y<this.exclude.end.y));
        }
    }

    /**
     * Generates positions
     *
     * @param Number num
     */
    generate(num) {
        this.blocks = [];
        for(let i = 0; i < num; i++) {
            let block;
            do {
                block = new Block((seedrandom())()*this.between.width,
                                    (seedrandom())()*this.between.height,
                                    this.size.width,
                                    this.size.height,
                                    this.fromCenter);
            } while(!this.valid(block));
            this.blocks.push(block);
        }
        return this.blocks;
    }
}

module.exports.Pos = Pos;
module.exports.Bounds = Bounds;
module.exports.Zone = Zone;
module.exports.Block = Block;
module.exports.Positions = Positions;