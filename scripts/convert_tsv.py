"""
Convert tsv files in https://github.com/cosylabiiit/Recipedb-companion-data
to spaCy v3 compatible .spacy format
"""

import csv
from tqdm import tqdm
from pathlib import Path

import spacy
from spacy.tokens import DocBin, Span

import srsly
import typer

from nltk.tokenize.treebank import TreebankWordDetokenizer



def read_tsv(tsv_path: Path):
    detok = TreebankWordDetokenizer()
    data = []
    with open(tsv_path) as tsvin:
        tsvin = csv.reader(tsvin, delimiter='\t')
        words, labels = [], []
        for row in tsvin:
            word, label = row
            if word == '' and label == '':
                if len(words) > 0 and len(labels) > 0:
                    sentence = detok.detokenize(words)
                    data.append([sentence, words, labels])
                    words, labels = [], []
            else:
                # handle special whitespace ' '
                if ' ' in word:
                    w1, w2 = word.split(' ')
                    words.append(w1)
                    words.append(w2)
                    labels.append(label)
                    labels.append(label)
                # handle dashes
                elif '-' in word and not word.startswith('-'):
                    words.append(word)
                    ws = word.split('-')
                    for i in range(2*len(ws)-1):
                        labels.append(label)
                else:
                    words.append(word)
                    labels.append(label)
                
    return data


def get_spans(labels):
    prev_label = None
    spans = []
    start = 0
    for i, label in enumerate(labels):
        if label not in ['QUANTITY', 'UNIT', 'NAME', 'DF', 'STATE', 'SIZE', 'TEMP']:
            if prev_label is not None:
                end = i
                spans.append((prev_label, [start, end]))
                prev_label = None
            continue
        if prev_label != label:
            if prev_label is None:
                start = i
            else:
                end = i
                spans.append((prev_label, [start, end]))
                start = i
        prev_label = label
        
    if prev_label is not None:
        end = len(labels)
        spans.append((prev_label, [start, end]))
        
    return spans


def convert(lang: str, input_path: Path, output_path: Path):
    data = read_tsv(input_path)
    nlp = spacy.blank(lang)
    db = DocBin()
    for text, _, labels in tqdm(data):
        doc = nlp.make_doc(text)
        spans = get_spans(labels)
        spans = [
            Span(doc, start, end, label) for label, (start, end) in spans
        ]
        doc.set_ents(spans)
        db.add(doc)
    db.to_disk(output_path)
    print("Saved output to:", output_path)



if __name__ == "__main__":
    typer.run(convert)