
import os
'''
Functions for removing the names from a text string.

The text file uniquenames.txt is required (unique first
and second names of students on Makerere graduation list,
with dictionary words removed).

@author John Quinn
@date 20-Feb-2012
'''
path=os.path.dirname(os.path.realpath(__file__))
def loadnames(namesfile='uniquenames.txt'):
    '''
    Load names into a dictionary object - hash table implementation
    has fast key lookup
    '''


    names = {}
    f = open(os.path.join(os.path.join(path,namesfile)),'r')
    for name in f.readlines():
        names[name.replace('\n','')] = ''
    return names

def removenames(text,names,replacewith='<anon>'):
    words = text.split()
    for i in range(len(words)):
        if names.has_key(words[i].lower()):
            words[i] = replacewith
    clean = ' '.join(words)
    return clean

if __name__=='__main__':
    # Demonstration of usage
    beforetxt = 'is it possible to marry your neighbour?, am ojara boniface from oyam'
    names = loadnames()
    aftertxt = removenames(beforetxt,names)
    print 'Before:', beforetxt
    print 'After:', aftertxt 

