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
async def main():
    async def idf(x):
        return x
    async def concat(x, y):
        return x + y
    async def toUpper(x):
        return x.upper()

    app.add('.id', idf, "Just the function that returns passed argument")
    app.add('.concat', concat, "Concatenate two strings")
    app.add('toUpper', toUpper, "To upper register")

    print(await app.exec('.id .toUpper .concat [First this, ] [Then that]'))

    print(await app.exec('.help'))
    print(await app.exec('.help toUpper'))
    print(await app.exec('.help help'))

    await app.exec('.allow help me')

import asyncio
asyncio.run(main())
