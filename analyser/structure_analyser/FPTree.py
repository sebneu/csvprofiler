__author__ = 'jumbrich'
from collections import defaultdict, namedtuple,Counter


class FPTree(object):
    """
    An FP tree.

    This object may only store transaction items that are hashable (i.e., all
    items must be valid as dictionary keys or set members).
    """

    Route = namedtuple('Route', 'head tail')

    def __init__(self):
        # The root node of the tree.
        self._root = FPNode(self, None, None)

        # A dictionary mapping items to the head and tail of a path of
        # "neighbors" that will hit every node containing that item.
        self._routes = {}

    @property
    def root(self):
        """The root node of the tree."""
        return self._root

    def add(self, transaction, label=""):
        """
        Adds a transaction to the tree.
        """

        point = self._root

        for item in transaction:
            next_point = point.search(item)
            if next_point:
                # There is already a node in this tree for the current
                # transaction item; reuse it.
                next_point.increment()
            else:
                # Create a new point and add it as a child of the point we're
                # currently looking at.
                next_point = FPNode(self, item)
                point.add(next_point)

                # Update the route of nodes that contain this item to include
                # our new node.
                self._update_route(next_point)
            next_point.addLabel(label)

            point = next_point

    def _update_route(self, point):
        """Add the given node to the route through all nodes for its item."""
        assert self is point.tree

        try:
            route = self._routes[point.item]
            route[1].neighbor = point # route[1] is the tail
            self._routes[point.item] = self.Route(route[0], point)
        except KeyError:
            # First node for this item; start a new route.
            self._routes[point.item] = self.Route(point, point)

    def items(self):
        """
        Generate one 2-tuples for each item represented in the tree. The first
        element of the tuple is the item itself, and the second element is a
        generator that will yield the nodes in the tree that belong to the item.
        """
        for item in self._routes.iterkeys():
            yield (item, self.nodes(item))

    def nodes(self, item):
        """
        Generates the sequence of nodes that contain the given item.
        """

        try:
            node = self._routes[item][0]
        except KeyError:
            return

        while node:
            yield node
            node = node.neighbor

    def prefix_paths(self, item):
        """Generates the prefix paths that end with the given item."""

        def collect_path(node):
            path = []
            while node and not node.root:
                path.append(node)
                node = node.parent
            path.reverse()
            return path

        return (collect_path(node) for node in self.nodes(item))

    def inspect(self):
        print 'Tree:'
        self.root.inspect(1)

        print
        print 'Routes:'
        for item, nodes in self.items():
            print '  %r' % item
            for node in nodes:
                print '    %r' % node

    def _removed(self, node):
        """Called when `node` is removed from the tree; performs cleanup."""

        head, tail = self._routes[node.item]
        if node is head:
            if node is tail or not node.neighbor:
                # It was the sole node.
                del self._routes[node.item]
            else:
                self._routes[node.item] = self.Route(node.neighbor, tail)
        else:
            for n in self.nodes(node.item):
                if n.neighbor is node:
                    n.neighbor = node.neighbor # skip over
                    if node is tail:
                        self._routes[node.item] = self.Route(head, n)
                    break



class FPNode(object):
    """A node in an FP tree."""

    def __init__(self, tree, item, count=1):
        self._tree = tree
        self._item = item
        self._count = count
        self._parent = None
        self.labels = []
        self._children = {}
        self._neighbor = None

    def add(self, child):
        """Adds the given FPNode `child` as a child of this node."""

        if not isinstance(child, FPNode):
            raise TypeError("Can only add other FPNodes as children")

        if not child.item in self._children:
            self._children[child.item] = child
            child.parent = self

    def search(self, item):
        """
        Checks to see if this node contains a child node for the given item.
        If so, that node is returned; otherwise, `None` is returned.
        """

        try:
            return self._children[item]
        except KeyError:
            return None

    def remove(self, child):
        try:
            if self._children[child.item] is child:
                del self._children[child.item]
                child.parent = None
                self._tree._removed(child)
                for sub_child in child.children:
                    try:
                        # Merger case: we already have a child for that item, so
                        # add the sub-child's count to our child's count.
                        self._children[sub_child.item]._count += sub_child.count
                        sub_child.parent = None # it's an orphan now
                    except KeyError:
                        # Turns out we don't actually have a child, so just add
                        # the sub-child as our own child.
                        self.add(sub_child)
                child._children = {}
            else:
                raise ValueError("that node is not a child of this node")
        except KeyError:
            raise ValueError("that node is not a child of this node")

    def __contains__(self, item):
        return item in self._children

    @property
    def tree(self):
        """The tree in which this node appears."""
        return self._tree

    @property
    def item(self):
        """The item contained in this node."""
        return self._item

    @property
    def count(self):
        """The count associated with this node's item."""
        return self._count

    def increment(self):
        """Increments the count associated with this node's item."""
        if self._count is None:
            raise ValueError("Root nodes have no associated count.")
        self._count += 1

    @property
    def root(self):
        """True if this node is the root of a tree; false if otherwise."""
        return self._item is None and self._count is None

    @property
    def leaf(self):
        """True if this node is a leaf in the tree; false if otherwise."""
        return len(self._children) == 0

    def parent():
        doc = "The node's parent."
        def fget(self):
            return self._parent
        def fset(self, value):
            if value is not None and not isinstance(value, FPNode):
                raise TypeError("A node must have an FPNode as a parent.")
            if value and value.tree is not self.tree:
                raise ValueError("Cannot have a parent from another tree.")
            self._parent = value
        return locals()
    parent = property(**parent())

    def neighbor():
        doc = """
        The node's neighbor; the one with the same value that is "to the right"
        of it in the tree.
        """
        def fget(self):
            return self._neighbor
        def fset(self, value):
            if value is not None and not isinstance(value, FPNode):
                raise TypeError("A node must have an FPNode as a neighbor.")
            if value and value.tree is not self.tree:
                raise ValueError("Cannot have a neighbor from another tree.")
            self._neighbor = value
        return locals()
    neighbor = property(**neighbor())

    @property
    def children(self):
        """The nodes that are children of this node."""
        return tuple(self._children.itervalues())

    def inspect(self, depth=0):
        print ('  ' * depth) + repr(self)
        for child in self.children:
            child.inspect(depth + 1)

    def __repr__(self):
        if self.root:
            return "<%s (root)>" % type(self).__name__
        return "<%s %r (%r)>" % (type(self).__name__, self.item, self.count)

    def addLabel(self, label):
        self.labels.append(label)


def buildCon( node, tree, docset, headerlist):
    headerlist.append(node.item)

    if node.leaf:
        tree[repr(headerlist)]= {'docs': list(docset), 'combs': {}, 'headers': headerlist}
        # print 'leaf',tree
        return

    for child in node.children:
        #  print ' ',node.item,'.child-', child
        docs = child.labels

        if len(docset.difference( docs )) != 0:
            inter = docset.intersection( docs )
            if repr(headerlist) not in tree:
                tree[repr(headerlist)]= {'docs': list(docset), 'combs': {}, 'headers': headerlist}

            subtree = tree[repr(headerlist)]['combs']
            buildCon(child, subtree, inter, [])


        else:
            #     print ' same docs, continue'
            buildCon(child, tree, docset, headerlist)


def printFPNode(node, depth=1):
    print 'P'
    print ('  ' * depth),node
    if node.leaf:
        return

    for child in node.children:
        #print ('  ' * depth) + child.item
        printFPNode(child, depth+1)

def printTree (tree, depth):

    print tree
    for n in tree:
        print ('  ' * depth) + repr(n)

        printTree(tree[n]['combs'],depth+1)


if __name__ == '__main__':


    res= {
        '1234': [ '1','2','3','4'],
        '234': [ '2','3','4'],
        '34': [ '3','5'],
        '41': [ '4'],
        '12342': [ '1','2','3','4'],
        '123': [ '1','3','4'],
        '34': [ '1','2'],
        '4': [ '1'],
    }

    c= Counter()
    for k,v, in res.items():
        c.update(v)

    cc = {}
    for k,v in c.iteritems():
        print k,v
        cc[k]=v

    print cc

    tr = FPTree()



    for k,v, in res.items():
        print 'before sort',v
        v.sort(key=lambda x: cc[x], reverse=True)
        print 'after',v
        tr.add(v,k)

    print 'DocTree:'
    tr.root.inspect(1)

    tree = {}
    for n in tr.root.children:
        headers = []
        docs = set(n.labels)

        print 'before',n.item,'-',tree
        buildCon(n, tree , docs, headers)
        print 'after',n.item,'-',tree

    print '------'


    printTree (tree, 1)

    #for child in t.root.children:
    #    print child

    # print 'HTree:'
    # ht.root.inspect(1)
    #
    #
    # print
    # print 'Routes:'
    # for item, nodes in t.items():
    #     print '  %r' % item
    #     for node in nodes:
    #         print '    %r' % node