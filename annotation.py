import spacy
from graphviz import Digraph
from difflib import SequenceMatcher as SM

def run_spacy(nlp, sentence):
    ret = []
    parsing = nlp(sentence)
    for token in parsing:
        word = token.text
        headword = token.head.i
        if headword == token.i:
            headword = 0
        else:
            headword = headword + 1
        ret.append([str(word), str(token.tag_),
                    str(headword), str(token.dep_)])
    return ret

def gen_trees():

    nlp1 = spacy.load('en_core_web_sm')
    nlp2 = spacy.load('en_core_web_md')
    nlp3 = spacy.load('en_core_web_lg')
    nlp4 = spacy.load('en_core_sci_sm')
    nlp5 = spacy.load('en_core_sci_md')
    nlp6 = spacy.load('en_core_sci_lg')

    fr = open('Joe.txt','r')
    for line in fr:
        text = line.strip('\r\n')
        if not text[1] == '#':
            continue
        sentence = text[2:]

        trees = []
        trees.append(run_spacy(nlp1, sentence))
        trees.append(run_spacy(nlp2, sentence))
        trees.append(run_spacy(nlp3, sentence))
        trees.append(run_spacy(nlp4, sentence))
        trees.append(run_spacy(nlp5, sentence))
        trees.append(run_spacy(nlp6, sentence))
        
    return trees

def plot1():
    plot_tree(gen1tree(), 3)

def gen1tree():
    
    nlp1 = spacy.load('en_core_sci_sm')
    fr = open('Joe.txt','r')
    for line in fr:
        text = line.strip('\r\n')
        if not text[1] == '#':
            continue
        sentence = text[2:]
        
    return run_spacy(nlp1, sentence)

def plot_tree(tree, method):
    
    methods = ["web_sm", "web_md", "web_lg", "sci_sm", "sci_md", "sci_lg"]

    data = []
    for row in tree:
        data.append(row)
    dot = Digraph()
    for i, row in enumerate(data):
        dot.node(str(i+1), row[0]+' ('+row[1]+')')
    for i, row in enumerate(data):
        dot.edge(row[2], str(i+1), row[3])
    dot.render(filename=methods[method]+'.gv', view=True)
    

def annotate(tree):
    tuples = []
    verbmods = ['xcomp','punct','pcomp','amod','intj','auxpass','aux','conj']
    postverbs = ['xcomp','pcomp','prt']
    preverbs = ['advcl','pcomp','amod','intj','auxpass','advmod','aux']
    cons = ['conj']
    dobs = ['nmod','acomp','attr']
    
    for i, word in enumerate(tree):
        if word[1].startswith('VB') and word[3] not in verbmods:
            sub = ['NIL']
            dob = ['NIL']
            verb = [word[0]]
            verbi = [str(i+1)]
            for t, word2 in enumerate(tree):
                if word2[2] in verbi:
                    if word2[1].startswith('VB') and word2[3] in cons:
                        verb.append(word2[0])
                        verbi.append(str(t+1))
            for s, word3 in enumerate(tree):
                if word3[2] in verbi:
                    if word3[3] in postverbs:
                        for v0, v in enumerate(verb):
                            verb[v0] = v + '_' + word3[0]
                    elif word3[3] in preverbs:
                        for v1, v in enumerate(verb):
                            verb[v1] = word3[0] + '_' + v
                    elif word3[3].startswith('nsubj'):
                        sub.append(word3[0])
                        for c, word5 in enumerate(tree):
                            if word5[2] == str(s+1) and word5[3] in cons:
                                sub.append(word5[0])
                            elif word5[2] == str(s+1) and word5[3] in dobs:
                                sub[len(sub)-1] = word5[0] + "::" + sub[len(sub)-1]
                            elif word5[2] == str(s+1) and word5[3] == 'amod':
                                sub[len(sub)-1] = word5[0] + "_" + sub[len(sub)-1]
                    elif word3[3].startswith('dobj') or word3[3] in dobs:
                        dob.append(word3[0])
                        for l, word4 in enumerate(tree):
                            if word4[2] == str(s+1) and word4[3] in cons:
                                dob.append(word4[0])
                            elif word4[2] == str(s+1) and word4[3] in dobs:
                                dob[len(dob)-1] = word4[0] + "::" + dob[len(dob)-1]
                            elif word4[2] == str(s+1) and word4[3] == 'amod':
                                dob[len(dob)-1] = word4[0] + "_" + dob[len(dob)-1]
                        
            if len(sub) > 1:
                sub.remove('NIL')
            if len(dob) > 1:
                dob.remove('NIL')
            for s in sub:
                for d in dob:
                    for v in verb:
                        tup = ['f', s, v, d]
                        tuples.append(tup)
            
    return tuples



def form(sentence):
    formatted = sentence.split()
    formatted[0] = formatted[0][:-1]
    formatted[1] = formatted[1][:-1]
    formatted.insert(0, 'f')
    
    return formatted
    
def compare(preds, reals):
    p = 0
    r = 0
    
    for pred in preds:
        score = 0
        for real in reals:
            s =  comp(pred, real)
            if s > score:
                score = s
        p+= score
        r+= 3
                
    return [p, r]

def comp(pred, real):
    tot = 0
    for i in range(1,4):
        tot += SM(None, pred[i], real[i]).ratio()
    return tot
    

def test(filename):
    fr = open(filename, 'r')
    openings = ['=','f','c','n']
    nlp = spacy.load('en_core_sci_sm')
    pred = 0
    real = 0
    predlist = []
    reallist = []
    
    for line in fr:
        sentence = line.strip('\r\n')
        if sentence[0] not in openings:
            predlist = annotate(run_spacy(nlp, sentence))
        elif sentence[0] == 'f':
            reallist.append(form(sentence[5:-1]))
        else:
            if predlist or reallist:
                results = compare(predlist, reallist)
                print(predlist, "\n")
                print(reallist)
                print(results, "\n\n\n")
                pred += results[0]
                real += results[1]
                predlist = []
                reallist = []
        
    return pred/real
                
        
            
            
            