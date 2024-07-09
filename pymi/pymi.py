from nltk.util import ngrams
from collections import Counter
import pickle
from tqdm import tqdm
import os
import math
import re
import numpy as np

class Node():
    def __init__(self, val=None, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
    
    def __repr__(self):
        return f'(value: {self.val}, left: {self.left}, right: {self.right})'

class Tree():
    def __init__(self, sentence, segmenter, type_='ami', show_mi_to=6):
        assert type_ in ['ami', 'mi'], 'type_ should be one of ["ami", "mi"]'
        assert len(sentence) >= 2, 'length of sentence should be larger than 1'
        doc = list(sentence)
        mis = []
        for ngram in segmenter.get_constructions(doc, 2):
            mis+=[segmenter.get_mi(tuple(ngram), type_=type_)]

        while mis:
            ind = mis.index(max(mis))
            object_1 = doc.pop(ind)
            object_2 = doc.pop(ind)
            if type(object_1)==str:
                object_1 = Node(val=object_1)
            if type(object_2)==str:
                object_2 = Node(val=object_2)
            if type_=='ami':
                doc.insert(ind, Node(val=str(round(mis.pop(ind), 100))[1:show_mi_to], left=object_1, right=object_2))
            if type_=='mi':
                doc.insert(ind, Node(val=str(round(mis.pop(ind), 100))[:show_mi_to], left=object_1, right=object_2))

        self.root = doc[0]

    def print(self, val="val", left="left", right="right"):
        def display(root, val=val, left=left, right=right):
            """Returns list of strings, width, height, and horizontal coordinate of the root."""
            # No child.
            if getattr(root, right) is None and getattr(root, left) is None:
                line = '%s' % getattr(root, val)
                width = len(line)+int((2/3)*len(re.findall(u'[\u4e00-\u9fff]', line)))
                height = 1
                middle = width // 2
                return [line], width, height, middle

            # Only left child.
            if getattr(root, right) is None:
                lines, n, p, x = display(getattr(root, left))
                s = '%s' % getattr(root, val)
                u = len(s)+int((2/3)*len(re.findall(u'[\u4e00-\u9fff]', s)))
                first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s
                second_line = x * ' ' + '|' + (n - x - 1 + u) * ' '
                shifted_lines = [line + u * ' ' for line in lines]
                return [first_line, second_line] + shifted_lines, n + u, p + 2, n + u // 2

            # Only right child.
            if getattr(root, left) is None:
                lines, n, p, x = display(getattr(root, right))
                s = '%s' % getattr(root, val)
                u = len(s)+int((2/3)*len(re.findall(u'[\u4e00-\u9fff]', s)))
                first_line = s + x * '_' + (n - x) * ' '
                second_line = (u + x) * ' ' + '|' + (n - x - 1) * ' '
                shifted_lines = [u * ' ' + line for line in lines]
                return [first_line, second_line] + shifted_lines, n + u, p + 2, u // 2

            # Two children.
            left, n, p, x = display(getattr(root, left))
            right, m, q, y = display(getattr(root, right))
            s = '%s' % getattr(root, val)
            u = len(s)+int((2/3)*len(re.findall(u'[\u4e00-\u9fff]', s)))
            first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s + y * '_' + (m - y) * ' '
            second_line = x * ' ' + '|' + (n - x - 1 + u + y) * ' ' + '|' + (m - y - 1) * ' '
            if p < q:
                left += [n * ' '] * int((q - p)*(3/3))
            elif q < p:
                right += [m * ' '] * int((p - q)*(3/3))
            zipped_lines = zip(left, right)
            lines = [first_line, second_line]

            
            char_count = 0
            for a, b in zipped_lines:
                char_count = len(re.findall(u'[\u4e00-\u9fff]', a))
                s = a
                s+=u * ' '
                s+=b
                char_count+=len(re.findall(u'[\u4e00-\u9fff]', b))
                lines+=[s]
                

            return lines, n + m + u, max(p, q) + 2, n + u // 2

        lines, *_ = display(self.root, val, left, right)
        
        for line in lines:
            if re.findall(u'[\u4e00-\u9fff]', line):
                items = []
                current_seg = ''

                for i in line:
                    if i==' ':
                        if ' ' in current_seg or not current_seg:
                            current_seg+=' '
                        else:
                            items+=[current_seg]
                            current_seg = ' '
                    else:
                        if ' ' in current_seg:
                            items+=[current_seg]
                            current_seg = i
                        else:
                            current_seg+=i
                items+=[current_seg]
                n_reduced_spaces = 0
                n_char_item = 0
                for item in items:
                    if ' ' in item:
                        n_spaces = len(item)
                        n_spaces = n_spaces - (round(n_char_item*1/3)-n_reduced_spaces)
                        
                        n_reduced_spaces+=(round(n_char_item*1/3)-n_reduced_spaces)
                        
                        print(' '*n_spaces, end='')
                    else:
                        if re.findall(u'[\u4e00-\u9fff]', item):
                            n_char_item+=1
                        print(item, end='')
                    
                print('')
            else:
                print(line)
            
class PyMi():
    def __init__(self, documents=None, mi_f=None, use_pickle=True):

        if use_pickle:
            self.document_f = documents
            with open(self.document_f, 'rb') as f:
                self.documents = pickle.load(f)
        
        else:
            self.documents = documents

        if mi_f:
            with open(mi_f, 'rb') as f:
                self.mi_dic = pickle.load(f)
        else:
            self.mi_dic = None
        
        print('Getting bigrams...')
        ngrams_ = []
        for doc in tqdm(self.documents):
            doc = list(ngrams(doc, 2))
            if doc:
                ngrams_+=[doc]

        self.ngrams = [pair for doc in ngrams_ for pair in doc]
        self.ngram_freq = Counter([pair for pair in self.ngrams])
        
        ngram_arr = []
        freq_arr = []
        for ngram, freq in self.ngram_freq.items():
            ngram_arr+=[ngram]
            freq_arr+=[freq]

        self.freq_arr = np.array(freq_arr)
        self.ngram_arr = np.array(ngram_arr)
        
        self.n_ngrams = len(self.ngrams)
        
        self.n_words = 0
        self.word_count = {}
        
        print('Getting word counts...')
        for doc in tqdm(self.documents):
            for word in doc:
                if word not in self.word_count:
                    self.word_count[word] = 1
                else:
                    self.word_count[word]+=1
                
                self.n_words+=1

    def sentence_to_tree(self, item, type_='ami', show_mi_to=6, idx=None):
        assert type_ in ['ami', 'mi'], 'type_ should be one of ["ami", "mi"]'
        if idx!=None:
            item = self.get_sentences_with_word(item, max_n_sentences=idx+1)[idx]
                
        return Tree(item, self, type_=type_, show_mi_to=show_mi_to)
    
    def get_sentences_with_word(self, word, max_n_sentences):
        sentences = []
        n_sentences = 0
        for doc in self.documents:
            if word in ''.join(doc):
                sentences+=[doc]
                n_sentences+=1
                if n_sentences==max_n_sentences:
                    break
        
        return sentences

    def get_prob_dic(self, ngram):
        w1, w2 = ngram

        w1_condition_arr_dic = (self.ngram_arr[:, 0] == w1).reshape(-1, 1)
        w2_condition_arr_dic = (self.ngram_arr[:, 1] == w2).reshape(-1, 1)

        condition_arr = np.concatenate([w1_condition_arr_dic, w2_condition_arr_dic], axis=1)
        prob_dic = {}

        for condition in ((True, True), (True, False), (False, True), (False, False)):
            freq = (np.all(condition_arr == condition, axis=1)*self.freq_arr).sum()
            prob_dic[condition] = freq / self.n_ngrams
        
        return prob_dic

    def save_mi_to_file(self, file_name='', type_='ami'):
        assert type_ in ['ami', 'mi'], 'type_ should be one of ["ami", "mi"]'
        if os.path.isfile(file_name):
            with open(file_name, 'rb') as f:
                mi_dic = pickle.load(f)
            
            print(f'Found existing {type_} file with {len(mi_dic)} ngrams.')
        
        else:
            mi_dic = {}

        if not file_name:
            if self.document_f:
                file_name = self.document_f.split('.')[0]+'_mi.pickle'
            else:
                file_name = 'mi.pickle'
        
        ngrams = list(set(self.ngrams))
        ngrams = [ngram_ for ngram_ in ngrams if ngram_ not in mi_dic]

        i = 0
        for ngram_ in tqdm(ngrams):

            mi_dic[ngram_] = self.get_mi(ngram_, type_=type_)
            i+=1
            
            if i%1000==0:
                with open(file_name, 'wb') as f:
                    pickle.dump(mi_dic, f)
        with open(file_name, 'wb') as f:
            pickle.dump(mi_dic, f)
        self.mi_dic = mi_dic
    
    def get_mi(self, ngram, type_='ami'):
        assert type_ in ['ami', 'mi'], 'type_ should be one of ["ami", "mi"]'
        if self.mi_dic and ngram in self.mi_dic:
            return self.mi_dic[ngram]
        
        word1, word2 = ngram
        
        p_word1 = self.word_count[word1] / self.n_words
        p_word2 = self.word_count[word2] / self.n_words

        if type_=='ami':
            prob_dic = self.get_prob_dic(ngram)
            
            mi = 0
            if prob_dic[(True, True)]:
                mi+=prob_dic[(True, True)]*math.log2(prob_dic[(True, True)] / (p_word1 * p_word2))
            
            if prob_dic[(False, True)]:
                mi+=prob_dic[(False, True)]*math.log2(prob_dic[(False, True)] / ((1-p_word1) * p_word2))
            
            if prob_dic[(True, False)]:
                mi+=prob_dic[(True, False)]*math.log2(prob_dic[(True, False)] / (p_word1 * (1-p_word2)))
                
            if prob_dic[(False, False)]:
                mi+=prob_dic[(False, False)]*math.log2(prob_dic[(False, False)] / ((1-p_word1) * (1-p_word2)))
            
            return mi

        if type_=='mi':
            p_ngram = self.ngram_freq[ngram] / self.n_ngrams
            
            return p_ngram / (p_word1 * p_word2)

    def get_constructions(self, text, length):
        if len(text)<length:
            return []
        if len(text)==length:
            return [text]
        text_len = len(text)
        arr = [text[idx:-(text_len-length)+idx] for idx in range(text_len-length)]+[text[text_len-length:]]
        return arr

    def segment_sentence(self, item, type_='ami', idx=None, threshold=.03, return_mi_groups=False, seg=''):
        assert type_ in ['ami', 'mi'], 'type_ should be one of ["ami", "mi"]'
        def segment(sentence, mis, indices):
            sentence = list(sentence)
            current_word = sentence.pop(0)
            segmented_sentence = []
            current_mi_group = []
            mi_groups = []

            for ind in indices[1:]:
                if ind==0:
                    if mis: current_mi_group+=[mis.pop(0)]
                    current_word+=seg+sentence.pop(0)
                else:
                    segmented_sentence+=[current_word]
                    current_word = sentence.pop(0)
                    mi_groups+=[current_mi_group]
                    current_mi_group = []
                    if mis: mis.pop(0)
            
            segmented_sentence+=[current_word]
            mi_groups+=[current_mi_group]
            if return_mi_groups:
                return segmented_sentence, mi_groups
            return segmented_sentence
        
        if idx!=None:
            item = self.get_sentences_with_word(item, max_n_sentences=idx+1)[idx]
        mis = []
        for ngram in self.get_constructions(item, 2):
            mis+=[self.get_mi(tuple(ngram), type_=type_)]
        indices = [1]
        for mi in mis:
            if mi>=threshold:
                indices+=[0]
            else:
                indices+=[1]
        return segment(item, mis, indices)

    def concat(self, sentence, type_='ami', for_plot=False):
        assert type_ in ['ami', 'mi'], 'type_ should be one of ["ami", "mi"]'
        ngrams = []
        mis = []
        for ngram in self.get_constructions(sentence, 2):
            ngrams+=[ngram]
            mis+=[self.get_mi(tuple(ngram), type_=type_)]
        
        sentence = list(sentence)
        
        if not for_plot:
            while mis:
                ind = mis.index(max(mis))
                sentence.insert(ind, [[sentence.pop(ind)], sentence.pop(ind)])
                mis.pop(ind)
            
            return sentence
        else:
            while mis:
                ind = mis.index(max(mis))
                sentence.insert(ind, [str(round(max(mis), 5)).replace('0.', '.'), [sentence.pop(ind)], sentence.pop(ind)])
                mis.pop(ind)
            
            return str(sentence).replace('\'', '').replace(', ', '')

    def get_distribution(self, start, end, n_points=150, data=None, type_='ami', auto_stop=False):
        assert type_ in ['ami', 'mi'], 'type_ should be one of ["ami", "mi"]'
        if not data:
            data = {
                'threshold': [],
                'n_words': [],
                'mean_word_percentage': []
            }
        
        x = np.logspace(np.log2(0+1), np.log2(100+1), n_points, base=2, endpoint=True) - 1
        x/=(100/(end-start))
        x+=start

        pbar = tqdm(x)

        last_mean_word_percentage = np.inf
        for threshold in pbar:
            if threshold in data['threshold']: continue
            word_percentages = []
            segmented_sentences = []

            for sentence in self.documents:
                segmented_sentence = self.segment_sentence(sentence, threshold=threshold, type_=type_)
                word_percentages+=[1/len(segmented_sentence)]
                segmented_sentences+=[segmented_sentence]
            
            mean_word_percentage = sum(word_percentages)/len(word_percentages)
            terms = Counter([word for sentence in segmented_sentences for word in sentence])
            data['threshold']+=[threshold]
            n_words = len(terms)
            data['n_words']+=[n_words]
            data['mean_word_percentage']+=[mean_word_percentage]
            pbar.set_description(f'threshold:{threshold}; word percentage:last––{last_mean_word_percentage} this––{mean_word_percentage}')
            if last_mean_word_percentage==mean_word_percentage and auto_stop: break
            last_mean_word_percentage = mean_word_percentage

        return data