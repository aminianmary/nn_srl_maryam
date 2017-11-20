from collections import Counter, defaultdict
import re, codecs

class ConllStruct:
    def __init__(self, entries, predicates):
        self.entries = entries
        self.predicates = predicates

    def __len__(self):
        return len(self.entries)

class ConllEntry:
    def __init__(self, id, form, lemma, pos, sense='_', parent_id=-1, relation='_', predicateList=dict(),
                 is_pred=False):
        self.id = id
        self.form = form
        self.lemma = lemma
        self.norm = normalize(form)
        self.lemmaNorm = normalize(lemma)
        self.pos = pos.upper()
        self.parent_id = parent_id
        self.relation = relation
        self.predicateList = predicateList
        self.sense = sense
        self.is_pred = is_pred

    def __str__(self):
        entry_list = [str(self.id+1), self.form, self.lemma, self.lemma, self.pos, self.pos, '_', '_',
                      str(self.parent_id),
                      str(self.parent_id), self.relation, self.relation,
                      '_' if self.sense == '_' else 'Y',
                      self.sense]
        for p in self.predicateList.values():
            entry_list.append(p)
        return '\t'.join(entry_list)

def vocab(conll_path, format):
    wordsCount = Counter()
    posCount = Counter()
    semRelCount = Counter()
    lemma_count = Counter()

    for sentence in read_conll(conll_path, format):
        wordsCount.update([node.norm for node in sentence.entries])
        posCount.update([node.pos for node in sentence.entries])
        for node in sentence.entries:
            if node.predicateList == None:
                continue
            if node.is_pred:
                lemma_count.update([node.lemma])
            for pred in node.predicateList.values():
                if pred!='?':
                    semRelCount.update([pred])
    return (wordsCount, lemma_count, {w: i for i, w in enumerate(wordsCount)},
            {p: i for i, p in enumerate(posCount)}, semRelCount.keys(),
            {l: i for i, l in enumerate(lemma_count)})

def read_conll(fh, format):
    if format=="conll09":
        sentences = codecs.open(fh, 'r').read().strip().split('\n\n')
        read = 0
        for sentence in sentences:
            words = []
            predicates = list()
            entries = sentence.strip().split('\n')
            for entry in entries:
                spl = entry.split('\t')
                predicateList = dict()
                is_pred = False
                if spl[12] == 'Y':
                    is_pred = True
                    predicates.append(int(spl[0]) - 1)

                for i in range(14, len(spl)):
                    predicateList[i - 14] = spl[i]

                words.append(
                    ConllEntry(int(spl[0]) - 1, spl[1], spl[3], spl[5], spl[13], int(spl[9]), spl[11], predicateList,
                               is_pred))
            read += 1
            yield ConllStruct(words, predicates)
        print (str(read)+ 'sentences read.')
    elif format=="conllu":
        sentences = codecs.open(fh, 'r').read().strip().split('\n\n')
        read = 0
        for sentence in sentences:
            words = []
            predicates = list()
            entries = sentence.strip().split('\n')
            for entry in entries:
                # ignore comments
                if not entry.startswith('#'):
                    spl = entry.split('\t')
                    # ignore multi-word expressions and empty nodes
                    if not '-' in spl[0] and not '.' in spl[0]:
                        predicateList = dict()
                        is_pred = False
                        if spl[8] == 'Y':
                            is_pred = True
                            predicates.append(int(spl[0]) - 1)

                for i in range(10, len(spl)):
                    predicateList[i - 10] = spl[i]

                words.append(
                    ConllEntry(int(spl[0]) - 1, spl[1], spl[2], spl[3], spl[9], int(spl[6]), spl[7], predicateList,
                               is_pred))
            read += 1
            yield ConllStruct(words, predicates)
        print (str(read) + 'sentences read.')

def read_conll09(fh):
    sentences = codecs.open(fh, 'r').read().strip().split('\n\n')
    read = 0
    for sentence in sentences:
        words = []
        predicates = list()
        entries = sentence.strip().split('\n')
        for entry in entries:
            spl = entry.split('\t')
            predicateList = dict()
            is_pred = False
            if spl[12] == 'Y':
                is_pred = True
                predicates.append(int(spl[0]) - 1)

            for i in range(14, len(spl)):
                predicateList[i - 14] = spl[i]

            words.append(
                ConllEntry(int(spl[0]) - 1, spl[1], spl[3], spl[5], spl[13], int(spl[9]), spl[11], predicateList,
                           is_pred))
        read += 1
        yield ConllStruct(words, predicates)
    print (str(read) + 'sentences read.')

def read_conllu(fh):
    sentences = codecs.open(fh, 'r').read().strip().split('\n\n')
    read = 0
    for sentence in sentences:
        words = []
        predicates = list()
        entries = sentence.strip().split('\n')
        for entry in entries:
            # ignore comments
            if not entry.startswith('#'):
                spl = entry.split('\t')
                # ignore multi-word expressions and empty nodes
                if not '-' in spl[0] and not '.' in spl[0]:
                    predicateList = dict()
                    is_pred = False
                    if spl[8] == 'Y':
                        is_pred = True
                        predicates.append(int(spl[0]) - 1)

            for i in range(10, len(spl)):
                predicateList[i - 10] = spl[i]

            words.append(
                ConllEntry(int(spl[0]) - 1, spl[1], spl[2], spl[3], spl[9], int(spl[6]), spl[7], predicateList,
                           is_pred))
        read += 1
        yield ConllStruct(words, predicates)
    print (str(read) +  'sentences read.')

def write_conll(fn, conll_structs):
    with codecs.open(fn, 'w') as fh:
        for conll_struct in conll_structs:
            for i in xrange(len(conll_struct.entries)):
                entry = conll_struct.entries[i]
                fh.write(str(entry))
                fh.write('\n')
            fh.write('\n')

numberRegex = re.compile("[0-9]+|[0-9]+\\.[0-9]+|[0-9]+[0-9,]+");
def normalize(word):
    return 'NUM' if numberRegex.match(word) else word.lower()

def get_scores(fp):
    line_counter =0
    labeled_f = 0
    unlabeled_f = 0
    with codecs.open(fp, 'r') as fr:
        for line in fr:
            line_counter+=1
            if line_counter == 10:
                spl = line.strip().split(' ')
                labeled_f = spl[len(spl)-1]
            if line_counter==13:
                spl = line.strip().split(' ')
                unlabeled_f = spl[len(spl) - 1]
    return (labeled_f, unlabeled_f)

