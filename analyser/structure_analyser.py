from analyser import Analyser

__author__ = 'jumbrich'
import logging
from collections import defaultdict, OrderedDict
from itertools import imap
from FPTree import FPTree, printFPNode
import networkx as nx
import urllib2

logger = logging.getLogger(__name__)


class StructureAnalyser(Analyser):
    def process(self, analyser_table):
        logger.debug('(%s) Structural analysis')

        dataset = []
        for row in analyser_table.rows:
            c_rows = []
            c=1
            for cell in row:
                if cell.empty:
                    value = ''
                else:
                    value = unicode(cell.value)
                c_row=hashdict({'col': c, 'value': value, 'label': str(c)+'_'+value, 'header': cell.column})
                #c_row=str(c)+'_col'+':'+cell

                c=c+1
                c_rows.append(c_row)
            dataset.append(c_rows)

        process1(analyser_table.name, dataset, len(analyser_table.columns), len(analyser_table.rows))


def process1(id, dataset, cols, rows):
    items = defaultdict(lambda: 0) # mapping from items to their supports
    processed_transactions = []

    # Load the passed-in transactions and count the support that individual
    # items have.
    for transaction in dataset:
        processed = []
        for item in transaction:
            items[item['label']] += 1
            processed.append(item)
        processed_transactions.append(processed)

    #for item, support in items.iteritems():
    #    print item, support
    # Remove infrequent items from the item support dictionary.
    items = dict((item, support) for item, support in items.iteritems()
        if support >= 1)

    # Build our FP-tree. Before any transactions can be added to the tree, they
    # must be stripped of infrequent items and their surviving items must be
    # sorted in decreasing order of frequency.
    def clean_transaction(transaction):
        transaction = filter(lambda v: v['label'] in items, transaction)
        transaction.sort(key=lambda v: items[v['label']], reverse=True)
        return transaction

    master = FPTree()

    for transaction in imap(clean_transaction, processed_transactions):
        #print transaction
        master.add(transaction)
    #plotTree(master)
    #printFPNode(master.root)

    plotTree(id, master, cols, rows)

def process(dataset):
    items = defaultdict(lambda: 0) # mapping from items to their supports
    processed_transactions = []

    # Load the passed-in transactions and count the support that individual
    # items have.
    for transaction in dataset:
        processed = []
        for item in transaction:
            items[item] += 1
            processed.append(item)
        processed_transactions.append(processed)

    #for item, support in items.iteritems():
    #    print item, support
    # Remove infrequent items from the item support dictionary.
    items = dict((item, support) for item, support in items.iteritems()
        if support >= 1)

    # Build our FP-tree. Before any transactions can be added to the tree, they
    # must be stripped of infrequent items and their surviving items must be
    # sorted in decreasing order of frequency.
    def clean_transaction(transaction):
        transaction = filter(lambda v: v in items, transaction)
        transaction.sort(key=lambda v: items[v], reverse=True)
        print 't'
        for t in transaction:
            print t
        return transaction

    master = FPTree()

    for transaction in imap(clean_transaction, processed_transactions):
        #print transaction
        master.add(transaction)

    print 'MASTER'
    print master
    #plotTree(master)
    printFPNode(master.root)

def parseGraph(treeNode, curNode, depth):


    print ('   -' * depth), treeNode
    if not treeNode.leaf:
        if len(treeNode.children) == 1:

            #merge nodes
            child = treeNode.children[0]

            node = Node(child)

            parseGraph(child, node, depth+1)

            if -1 not in curNode.cols:
                print ('    ' * (depth-1)),'  * M ',curNode.cols, node.cols
                curNode.merge(node)
                print ('    ' * (depth-1)),'  * MD ',curNode.cols, curNode.freq
            else:
                print ('    ' * (depth-1)),'  * MR ',curNode.cols, node.cols
                curNode.branch(node)
        else:

            for child in treeNode.children:
                #new node
                node = Node(child)
                parseGraph(child, node, depth+1)
                print ('    ' * (depth-1)),'  - B ',curNode.cols,curNode.freq, 'with', node.cols, node.freq
                curNode.branch(node)
            curNode.summarise()
            print ('    ' * (depth-1)),'  - S ',curNode.children
    else:
        #print 'leaf'
        pass







def buildCompressedGraph(curNode, fromLabel, toLabels, G, id, freq, depth=1):
    print ('   -' * depth),curNode

    if curNode.leaf:
        #at the end of a branch
        id=id+1
        if len(toLabels)>1:
            tlabel= 'cols['+','.join(sorted(map(str,toLabels)))+']'
            tlabel= str(len(toLabels))+' cols'
        else:
            tlabel= 'col_'+''.join(toLabels)

        print ('    ' * depth),'Create edge, leaf ', fromLabel,' ->', tlabel
        tlabel =tlabel+' (f:'+str(freq)+'#'+str(id)+')'
        G.add_node(tlabel)
        G.add_edge(fromLabel, tlabel)

    else:
        if len(curNode.children) == 1:
            #no branching
            child = curNode.children[0]
            if child.item:
                l= child.item['col']
                nlabel= l
            else:
                nlabel=':'+str(id)
            toLabels.append(nlabel)
            id = buildCompressedGraph(child, fromLabel, toLabels, G, id,child.count,depth+1)
        else:
            #branching
            id=id+1
            if len(toLabels)>1:
                tlabel= 'cols['+','.join(sorted(map(str,toLabels)))+']'
                tlabel= str(len(toLabels))+' cols'
            else:
                tlabel= 'col_'+''.join(map(str,toLabels))
            tlabel =tlabel+' (f:'+str(freq)+'#'+str(id)+')'

            print ('    ' * (depth-1)),'  *','Create edge, Branch ', fromLabel,' ->', tlabel
            G.add_node(tlabel)
            G.add_edge(fromLabel, tlabel)
            fromLabel=tlabel

            for child in curNode.children:

                if child.item:
                    l= child.item['col']
                    nlabel= l
                else:
                    nlabel=':'+str(id)
                toLabels=[]
                toLabels.append(nlabel)

                id = buildCompressedGraph(child, fromLabel, toLabels, G, id, child.count, depth+1)
    return id

def buildGraph(nodeLabel, curNode, G, id):
    id=id+1
    if not curNode.leaf:
        for child in curNode.children:
            if child.item:
                nlabel= child.item['label']+'('+str(child.count)+'):'+str(id)
            else:
                nlabel='_id'+str(id)
            G.add_node(nlabel)
            G.add_edge(nodeLabel, nlabel)
            #print ('  ' * depth) + child.item
            id=buildGraph(nlabel, child, G, id)

    return id

def buildAccessGraph(nodeLabel, curNode, G, id):
    id=id+1
    for child in curNode.children:

        nlabel=child.toNodeString()+'\\n(#id'+str(id)+')'
        G.add_node(nlabel)
        G.add_edge(nodeLabel, nlabel)
        #print ('  ' * depth) + child.item
        id=buildAccessGraph(nlabel, child, G, id)

    return id

def printTTree(tree, depth=1):
    #print tree.cols, tree.freq
    print 'Tree'
    for n in tree.children:
        print 'child',n
        print ('  ' * depth),n.cols, n.freq, n.distinct
        #print ('  ' * depth) + repr(n)
        printTTree(n,depth+1)



def plotTree(id, master, cols=0, rows=0):
    
    c=0
    nodeFrom = id+'\\n ('+str(cols)+' cols, '+str(rows)+'rows)'
    
    #full graph
    G=nx.DiGraph()
    G.add_node(nodeFrom)
    buildGraph(nodeFrom, master.root, G, c)
    
    G1=nx.DiGraph()
    G1.add_node(nodeFrom)
    buildCompressedGraph(master.root, nodeFrom, [],  G1, c, master.root.count)
    

    node = Node(master.root, freq=rows)
    parseGraph(master.root, node, depth=1)

    printTTree(node)
    G2=nx.DiGraph()
    G2.add_node(nodeFrom)
    buildAccessGraph(nodeFrom, node, G2,c)

    

    A = nx.to_agraph(G)
    A.layout('dot', args='-Nfontsize=10 -Nwidth=".2" -Nheight=".2" -Nmargin=0 -Gfontsize=8')
    A.draw(urllib2.quote(id, '')+'_raw.png')

    A = nx.to_agraph(G1)
    A.layout('dot', args='-Nfontsize=10 -Nwidth=".2" -Nheight=".2" -Nmargin=0 -Gfontsize=8')
    A.draw(urllib2.quote(id, '')+'_sum.png')

    A = nx.to_agraph(G2)
    A.layout('dot', args='-Nfontsize=10 -Nwidth=".2" -Nheight=".2" -Nmargin=0 -Gfontsize=8')
    A.draw(urllib2.quote(id, '')+'_acc.png')
        # F = []
        # support_data = {}
        # for k,v in fpgrowth.find_frequent_itemsets(rows, min_support=0.5, include_support=True, verbose=True):
        #     F.append(frozenset(k))
        #     support_data[frozenset(k)] = v
        #
        # # Create one array with subarrays that hold all transactions of equal length.
        # def bucket_list(nested_list, sort=True):
        #     bucket = defaultdict(list)
        #     for sublist in nested_list:
        #         bucket[len(sublist)].append(sublist)
        #     return [v for k,v in sorted(bucket.items())] if sort else bucket.values()
        #
        # F = bucket_list(F)
        #
        # print F
        # print support_data
        #

        #F, support = fpgrowth.fpgrowth(rows,min_support=0.1, include_support=True, verbose=True)
        #print F
        #print support

        # import apriori
        # import fpGrowth
        #
        # from fp_growth import find_frequent_itemsets
        # for itemset, support in find_frequent_itemsets(rows, 3, True):
        #     print '{' + ', '.join(itemset) + '} ' + str(support)+' ('+str(support/(len(rows)*1.0))+')'
        #
        # print '_____'
        #
        # myFPtree, myHeaderTab = fpGrowth.createTree(fpGrowth.createInitSet(rows),3)
        # #myFPtree.disp()
        # #print(findPrefixPath('r', myHeaderTab['r'][1]))
        # freqItems = []
        # #fpGrowth.mineTree(myFPtree, myHeaderTab, 3, set([]), freqItems)
        # #print 'freqItems:',freqItems
        #
        # L, results= apriori.apriori(rows,minsupport=0.1)
        #
        # for rule in apriori.generateRules(L, results, min_confidence=0.8):
        #     print rule

class hashdict(dict):
    """
    hashable dict implementation, suitable for use as a key into
    other dicts.

        >>> h1 = hashdict({"apples": 1, "bananas":2})
        >>> h2 = hashdict({"bananas": 3, "mangoes": 5})
        >>> h1+h2
        hashdict(apples=1, bananas=3, mangoes=5)
        >>> d1 = {}
        >>> d1[h1] = "salad"
        >>> d1[h1]
        'salad'
        >>> d1[h2]
        Traceback (most recent call last):
        ...
        KeyError: hashdict(bananas=3, mangoes=5)

    based on answers from
       http://stackoverflow.com/questions/1151658/python-hashable-dicts

    """
    def __key(self):
        return tuple(sorted(self.items()))
    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__,
            ", ".join("{0}={1}".format(
                    str(i[0]),repr(i[1])) for i in self.__key()))

    def __hash__(self):
        return hash(self.__key())
    def __setitem__(self, key, value):
        raise TypeError("{0} does not support item assignment"
                         .format(self.__class__.__name__))
    def __delitem__(self, key):
        raise TypeError("{0} does not support item assignment"
                         .format(self.__class__.__name__))
    def clear(self):
        raise TypeError("{0} does not support item assignment"
                         .format(self.__class__.__name__))
    def pop(self, *args, **kwargs):
        raise TypeError("{0} does not support item assignment"
                         .format(self.__class__.__name__))
    def popitem(self, *args, **kwargs):
        raise TypeError("{0} does not support item assignment"
                         .format(self.__class__.__name__))
    def setdefault(self, *args, **kwargs):
        raise TypeError("{0} does not support item assignment"
                         .format(self.__class__.__name__))
    def update(self, *args, **kwargs):
        raise TypeError("{0} does not support item assignment"
                         .format(self.__class__.__name__))
    def __add__(self, right):
        result = hashdict(self)
        dict.update(result, right)
        return result


class Node():
    def __init__(self, treeNode=None, accessNode=None, freq=None):
        #print treeNode.item
        #print dir(treeNode)
        if treeNode:

            if freq:
                self.freq= freq
            else:
                self.freq= treeNode.count
            if not treeNode.item:
                self.cols =[-1]
                self.value=['root']
            else:
                self.cols =[treeNode.item['col']]
                self.value=[treeNode.item['value']]
                print treeNode.item['header']
                self.header=[treeNode.item['header']]
                
            self.children=[]
            self.distinct=1
        elif accessNode:
            self.freq= accessNode.freq
            self.cols =accessNode.cols
            self.value=[]
            self.header = accessNode.header
            self.children=accessNode.children
            self.distinct=0
        self.groups={}

    def merge(self, node):

        self.cols=self.cols+node.cols
        self.value=self.value+node.value
        if self.freq != node.freq:
            print "ERROR, freqs should be same", self.freq, node.freq
    def branch(self, node):
        self.children.append(node)
    def summarise(self):
        #check if the child have the same col structure

        for node in self.children:
            #check if
            if len(set(node.cols)) != len(node.cols):
                print "ERROR; duplicate cols in node"
            else:
                #print sorted(node.cols)
                id = node.dfscode()
                if id not in self.groups:
                    self.groups[id]= Node(accessNode=node)
                self.groups[id].distinct+=1

        self.children=[]
        for g in self.groups:
           self.children.append(self.groups[g])

    def __str__(self):
        return 'cols['+','.join(map(str,sorted(self.cols)))+"]:freq:"+str(self.freq)+':dist:'+str(self.distinct)

    def toNodeString(self):
        s=""
        if len(self.cols) ==1:
            s+= '('+''.join(map(str,sorted(self.header)))+")\\n"
            s+='col '+''.join(map(str,sorted(self.cols)))+"\\n"
        else:
            s+='cols['+','.join(map(str,sorted(self.cols)))+"]\\n"
        s+= "freq:"+str(self.freq)+' distinct:'+str(self.distinct)

        return s

    def dfscode(self):
        code = ','.join(map(str,sorted(self.cols)))+":"+str(self.freq)+':'+str(self.distinct)

        d = {}
        for node in self.children:
            id = ','.join(map(str,sorted(node.cols)))+":"+str(node.freq)+':'+str(node.distinct)
            d[id]= node
        od = OrderedDict(sorted(d.items()))
        for k, v in od.iteritems():
            code+='@'+v.dfscode()
        return code