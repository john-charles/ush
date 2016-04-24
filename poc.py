#!/usr/bin/env python

class String:
    value = None

    def __init__(self, value):
        self.value = value

class Number:
    value = None

    def __init__(self, value):
        self.value = value

class Boolean:
    value = None

    def __init__(self, value):
        value = value

class Array:

    value = None

    def __init__(self):
        self.value = []

class Map:

    value = None

    def __init__(self):
        self.value = {}

class Function:

    name = None
    statements = None

    def __init__(self, name, statements):
        self.name = name
        self.statements = statements

    def evaluate(self, scope):
        pass


class Scope:

    parent = None
    values = None
    commands = None

    def __init__(self, parent):
        self.parent = parent
        self.values = {}
        self.commands = {}

    def resolve_value(self, key):

        if key in self.values:
            return self.values[key]
        elif self.parent:
            return self.parent.resolve_value(key)
        else:
            return None

    def resolve_command(self, key):

        if key in self.commands:
            return self.commands[key]
        elif self.parent:
            return self.parent.resolve_command(key)
        else:
            return None

    def assign_value(self, key, value):
        self.values[key] = value

    def assign_command(self, key, command):
        self.commands[key] = command

class Statement:

    parts = None

    def __init__(self, parts):
        self.parts = parts

    def evaluate(self, scope):
        pass





class WordReader:

    stream = None
    file_name = None

    eos = ['\n', ';']
    specials = ['(', ')']
    secquence = ['\'', '"']

    def __init__(self, file):
        self.file_name = file
        self.stream = open(file, 'rb')
        self.last_words = []

    def read_triplet_secquence(self, triplet):

        secquence = ''

        while not secquence.endswith(triplet):
            char = self.stream.read(1)
            if not char:
                raise Excepton("Unexpected EOF")
            
            secquence += char

        return triplet + secquence
   
    def read_secquence(self, first):
         
        is_escaped = False
        secquence = str(first)
       
        while True:
            char = self.stream.read(1)
            if not char:
                raise Exception("Unexpected eof")

            if char == '\\':
                is_escaped = True
            elif is_escaped:
                secquence += char
                is_escaped = False
            elif char == first and len(secquence) == 1:
                nxt = self.stream.read(1)
                if nxt == first:
                    return self.read_triplet_secquence(first * 3)
            elif char == first:
                return secquence + char
            else:
                secquence += char 
         

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
            elif char in self.specials and word:
                self.last_words.append(char)
                return word
            elif char in self.secquence and word:
                raise Exception("Syntax Error, %s%s is invalid!" % (word, char))
            elif char in self.secquence:
                return self.read_secquence(char) 
            elif char in self.specials and not word:
                return char
            elif char not in eow and char not in self.eos:
                word += char

    def put_word(self, word):
        self.last_words.append(word)
        
class Processor:
   
    reserved = None
    word_reader = None

    def __init__(self, file_name):
        self.word_reader = WordReader(file_name)

        self.reserved = {
                "if": self.process_if,
                "function": self.process_function
        }

        self.functions = {
        }

        self.values = {}

    def evaluate_single_statement(self, statement):

        if statement[0][0] == '$' and len(statement) == 3 and statement[1] == '=':
            self.values[statement[0]] = statement[2]

        


    def evaluate(self, statement):

        print "Evaluating statement: ", statement

        if len(statement) == 1 and isinstance(statement[0], dict):
            print "Evaluating a block generator...."
            
            generator = statement[0]

            if 'name' in generator:
                self.functions[generator['name']] = generator


            
        else:
            print "Evaluating a standard statement..."



    def collect_statement_until(self, end):

        statement = []
        statements = []

        while True:

            word = self.word_reader.get_word()
            if not word:
                raise Exception("Expected more code...")

            if word == end:
                if len(statement) > 0:
                    statements.append(statement)
                return statements

            if word in self.word_reader.eos:
                if len(statement) > 0:
                    statements.append(statement)
                statement = []

            elif word in self.reserved:
                statement.append(self.reserved[word]())
            else:
                statement.append(word)

    def process_if(self):
        
        else_body = None
        word = self.word_reader.get_word()

        if word != '(':
            raise Exception("Expected '(' got '%s'" % word)

        clause = self.collect_statement_until(')')

        word = self.word_reader.get_word()

        if word != '{':
            raise Exception("Expected '{' got '%s'" % word)

        body = self.collect_statement_until('}')

        word = self.word_reader.get_word()

        if word != 'else':
            self.word_reader.put_word(word)
        else:
            word = self.word_reader.get_word()
            if word != '{':
                raise Exception("Expected '{' got '%s'" % word)
            else_body = self.collect_statement_until('}')


        return {
            "cluase": clause,
            "body": body,
            "else_body": else_body
        }

    def process_function(self):

        name = self.word_reader.get_word()
        word = self.word_reader.get_word()

        if word != '{':
            raise Exception("Expected '{'got '%s'" % word)

        body = self.collect_statement_until('}')

        return {
            "name": name,
            "body": body
        } 
    
    def process(self):

        statement = []

        while True:
            
            word = self.word_reader.get_word()
            if not word:
                break

            if word in self.word_reader.eos:
                self.evaluate(statement)
                statement = []

            if word not in self.reserved and word not in self.word_reader.eos:
                statement.append(word)

            if word and word in self.reserved:
                statement.append(self.reserved[word]())
        

if __name__ == '__main__':
   
    processor = Processor("poc.ush") 
    processor.process()

