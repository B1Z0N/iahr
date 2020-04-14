from app import *


def test_query(qstr):
    q = Query.from_str(qstr)
    def print_query(q):
        print("Command:", q.command)
        if type(q.args) == type([]):
            print("Args:", q.args)
        elif q.args is None:
            pass
        else: 
            print_query(q.args)
        
    print_query(q)

# test_query(input())

app.add('.id', lambda x: x, "Just the function that returns passed argument")
app.add('.concat', lambda x, y: x + y, "Concatenate two strings")
app.add('toUpper', lambda x: x.upper(), "To upper register")

print(app.exec('.id .toUpper .concat [First this, ] [Then that]'))

print(app.exec('.help'))
print(app.exec('.help toUpper'))
print(app.exec('.help help'))

app.exec('.allow help me')
