#!/usr/bin/env python

class String:
    value = None

    def __init__(self, value):
        self.value = value

    def evaluate(self, scope):
        pass

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

class ArrayDecleration:
    
    statements = None

    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return "ArrayDecleration(%s)" % self.statements

class Map:

    value = None

    def __init__(self):
        self.value = {}

class MapDecleration:

    statements = []

    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return "MapDecleration(%s)" % self.statements

class Command:

    name = None
    statements = None

    def __init__(self, name, statements):
        self.name = name
        self.statements = statements

    def evaluate(self, scope):
        print "Evaluating command: ", self.name, self.statements
        scope.assign_command(self.name, self)
        pass

    def execute(self, scope):
        pass


class Function:

    name = None
    statements = None

    def __init__(self, name, statements):
        self.name = name
        self.statements = statements

    def __repr__(self):
        return "Function(name=%s, statements=%s)" % (
                self.name, self.statements)

    def evaluate(self, scope):
        print "Evaluationg function: ", self.name, self.statements
        scope.assign_command(self.name, self)
        pass

    def execute(self, scope):
        pass


class Scope:

    parent = None
    values = None
    commands = None

    def __init__(self, parent=None):
        self.parent = parent
        self.values = {}
        self.commands = {}

    def __repr__(self):
        return "Scope(parent=%s)" % self.parent

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

    def __repr__(self):
        return "Statement(%s)" % self.parts
    def evaluate(self, scope):
        print 'evaluating: ', self.parts, scope
        pass

class Decision:

    clause = None
    main_body = None
    else_body = None

    def __init__(self, clause, main_body, else_body):
        self.clause = clause
        self.main_body = main_body
        self.else_body = else_body

    def __repr__(self):
        
        return "Decision(clause=%s, body=%s, else=%s)" % (
                self.clause, self.main_body, self.else_body)

    def evaluate(self, scope):
        print "Evaluating decison: ", self.clause, self.main_body, self.else_body
        pass



class WordReader:

    stream = None
    file_name = None

    eos = ['\n', ';']
    specials = ['(', ')', ':', ',', '[',']']
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
                "command": self.process_command,
                "function": self.process_function
        }


    def collect_statement_until(self, end):

        statement = []
        statements = []

        while True:

            word = self.word_reader.get_word()
            
            if not word:
                raise Exception("Expected more code...")

            if word == end:
                if len(statement) > 0:
                    statements.append(Statement(statement))
                return statements

            if word in self.word_reader.eos:
                if len(statement) > 0:
                    statements.append(Statement(statement))
                statement = []

            elif word == '{':
                statement.append(MapDecleration(self.collect_statement_until('}')))
            
            elif word == '[':
                statement.append(ArrayDecleration(self.collect_statement_until(']')))

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

        return Decision(clause, body, else_body)

    def process_function(self):

        name = self.word_reader.get_word()
        if name == '{':
            name = "<anonymoust>"
        else:

            word = self.word_reader.get_word()

            if word != '{':
                raise Exception("Expected '{'got '%s'" % word)

        body = self.collect_statement_until('}')

        return Function(name, body)
    
    def process_command(self):

        name = self.word_reader.get_word()
        word = self.word_reader.get_word()

        if word != '{':
            raise Exception("Expected '{'got '%s'" % word)

        body = self.collect_statement_until('}')

        return Command(name, body)

    def process(self):

        scope = Scope()
        statement = []

        while True:
            
            word = self.word_reader.get_word()
            if not word:
                break

            if word in self.word_reader.eos:
                Statement(statement).evaluate(scope)
                statement = []

            elif word == '{':
                statement.append(MapDecleration(self.collect_statement_until('}')))
            elif word == '[':
                statement.append(ArrayDecleration(self.collect_statement_until(']')))

            elif word not in self.reserved and word not in self.word_reader.eos:
                statement.append(word)

            elif word and word in self.reserved:
                complex = self.reserved[word]()
                complex.evaluate(scope)
        

if __name__ == '__main__':
  
    import sys

    processor = Processor(sys.argv[1]) 
    processor.process()

