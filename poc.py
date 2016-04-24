#!/usr/bin/env python

class WordReader:

    stream = None
    file_name = None

    eos = ['\n', ';']

    def __init__(self, file):
        self.file_name = file
        self.stream = open(file, 'rb')
        self.last_words = []
    

    def get_word(self):

        if len(self.last_words):
            return self.last_words.pop()

   
        word = ''
        eow = [' ', '\t', '\r', '\b']
 
        while True:
            char = self.stream.read(1)
            if not char:
                return word

            if char in eow and word:
                return word
            elif char in self.eos and word:
                self.last_words.append(char)
                return word
            elif char in self.eos and not word:
                return char 
            elif char not in eow and char not in self.eos:
                word += char
        

def process(word_reader):
    reserved = {
    } 

    statement = []

    while True:
        
        word = word_reader.get_word()
        if not word:
            break

        if word in word_reader.eos:
            print "Would evaluate statement: ", statement
            statement = []

        if word not in reserved and word not in word_reader.eos:
            statement.append(word)

    return statement
        
        
        
        

if __name__ == '__main__':
   
    word_reader = WordReader("poc.ush") 
    process(word_reader)

