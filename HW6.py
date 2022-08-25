from os import sys, path
import numpy as np

class Suffix_Tree:
    def __init__(self, value = '', father = None):
        self.value = value
        self.children = dict()
        self.father = father
        self.frequent_set = set()

    def get_sup(self):
        return len(self.frequent_set)

    def add_frequent_item(self, item, commons):
        node = self
        for common in commons:
            if common == '':
                node.frequent_set.add(item)
            else:
                node.children[common].frequent_set.add(item)
                node = node.children[common]

    def find_father(self, value, common = ''):
        if value == self.value:
            return self, '', common

        for child_name, child in self.children.items():
            if child_name[0] == value[0]:
                common_prefix = path.commonprefix([value, child_name])
                common += ',' + common_prefix
                if len(common_prefix) == len(child_name):
                    return child.find_father(value[len(common_prefix):], common)
                return child, value[len(common_prefix):], common

        return self, value, common

    def add_child(self, value, item_number):

        father, uncommon, common = self.find_father(value)
        common = common.split(',')
        if uncommon:
            if father.value == common[-1]:
                father.children[uncommon] = Suffix_Tree(uncommon, father)
            else:
                old_value = father.value
                new_father = Suffix_Tree(common[-1], father.father)
                new_father.frequent_set.update(list(father.frequent_set))
                new_father.children[uncommon] = Suffix_Tree(uncommon, new_father)
                new_father.children[old_value[len(common[-1]):]] = father.father.children.pop(old_value)
                new_father.children[old_value[len(common[-1]):]].value = old_value[len(common[-1]):]

                father.father.children[new_father.value] = new_father
                father.father.children[new_father.value].children[old_value[len(common[-1]):]].father = father.father.children[new_father.value]
            common.append(uncommon)
        self.add_frequent_item(item_number, common)

def suffix(sequencedb, Tree):
    sequencedb = np.char.add(sequencedb, '$')
    for sequence_index, sequence in enumerate(sequencedb):
        for j in range(len(sequence)-1):
            Tree.add_child(sequence[j:], sequence_index)

def get_sup(Tree:Suffix_Tree, substr:str):
    if not substr:
        return Tree.get_sup()
    for child_value, child in Tree.children.items():
        cv = child_value.replace('$', '')
        if len(cv) == 0:
            continue
        if cv[0] != substr[0]:
            continue
        if substr == cv:
            return child.get_sup()
        elif len(substr) <= len(cv):
            if len(path.commonprefix([substr, cv])) == len(substr):
                return child.get_sup()
            return 0
        else:
            if cv == substr[:len(cv)]:
                return get_sup(child, substr[len(cv):])
            return 0
    return 0

def find_cfs(Tree, MINSUP, cfs, fathers = ''):
    value = fathers + Tree.value.replace('$', '')
    if Tree.get_sup() < MINSUP:
        return
    exists = False
    for itemset in list(cfs):
        if itemset in value and cfs[itemset] >= Tree.get_sup():
            cfs.pop(itemset)
    for itemset, sup in cfs.items():
        its = itemset.replace('$', '')
        if value not in its:
            continue
        if Tree.get_sup() < sup:
            cfs[value] = Tree.get_sup()
            exists = True
            break   
    if not exists:
        cfs[value] = Tree.get_sup()
    for child in Tree.children.values():
        find_cfs(child, MINSUP, cfs, value)

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Bad Call")
        exit(-1)

    sequencedb_path   =   sys.argv[1]
    seqin_path        =   sys.argv[2]

    sequencedb  =   np.loadtxt(sequencedb_path, dtype=str, comments='>', delimiter='\n')
    seqin       =   np.loadtxt(seqin_path, dtype=str, delimiter='\n')
    MINSUP      =   10

    Tree = Suffix_Tree()

    suffix(sequencedb, Tree)

    cfs = dict()

    find_cfs(Tree, MINSUP, cfs)
    
    for seq in seqin:
        print(seq, '-', get_sup(Tree, seq))

    print('closed_frequent_substring:')
    for itemset, sup in cfs.items():
        print(itemset, '-', sup)
