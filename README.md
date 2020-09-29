# Research
Information Extraction code I worked on to parse information from COVID-19 scientific journals

The code uses the spacy library to first generate a word tree based on inputted sentences. 
The plot_Tree run_spacy and gen_trees functions were coded by my advisor Dr. Meng Jiang (Notre Dame)
I use the tree from these code and pass it into my funtion 'annotate' This funciton forms fact tuples
based on the tree of words that is inputted. I then devloped the following 4 functions in order to test
my 'annotate' funciton. This code is specific to the formatted tuples of preannotated journals that we 
use as a benchmark.
