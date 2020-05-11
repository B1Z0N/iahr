import pytest

from iahr.run import Query, Routine, Executer
from iahr.run import CommandSyntaxError, PermissionsError, \
    ExecutionError, NonExistantCommandError

idx = lambda x : x
about = 'something'

@pytest.mark.parametrize('chat, usr', [
    ('chat', 'usr'),
    ('chat', 'chat')
])
def test_routine(chat, usr):
    rt = Routine(idx, about)

    assert rt.is_allowed_chat(chat) and not rt.is_allowed_usr(usr) 
    assert not rt.get_handler(usr, chat)
    rt.allow_chat(chat)
    assert rt.is_allowed_chat(chat) and not rt.is_allowed_usr(usr)
    assert not rt.get_handler(usr, chat)
    rt.ban_chat(chat)    
    assert not rt.is_allowed_chat(chat) and not rt.is_allowed_usr(usr)
    assert not rt.get_handler(usr, chat)
    rt.allow_usr(usr)
    assert not rt.is_allowed_chat(chat) and rt.is_allowed_usr(usr)
    assert not rt.get_handler(usr, chat)
    rt.allow_chat(chat)
    print(rt.usraccess, rt.chataccess)
    assert rt.is_allowed_chat(chat) and rt.is_allowed_usr(usr)
    assert rt.get_handler(usr, chat) == idx
    assert rt.help() == about


qtest_data = [
    # simple
    ('.do', Query('do')),
    # arg tests
    ('.do this', Query('do', ['this'])),
    ('.do [this]', Query('do', ['this'])),
    ('[.do [this]]', Query('do', ['this'])),
    # multiword and multiarg tests
    ('[.do [this multi]]', Query('do', ['this multi'])),
    ('[.do [  this multi] [and] [this]]', Query('do', ['  this multi', 'and', 'this'])),
    # subcommand tests
    ('.do .do1', Query('do', [Query('do1')])),
    ('.do [.do1]', Query('do', [Query('do1', )])),
    ('[.do [.do1]]', Query('do', [Query('do1', )])),
    # subcommand args tests
    ('.do .do1 this', Query('do', [Query('do1', ['this'])])),
    ('.do .do1 [this]', Query('do', [Query('do1', ['this'])])),
    ('[.do .do1 [this]]', Query('do', [Query('do1', ['this'])])),
    ('[.do .do1 [this] .do2]', Query('do', [Query('do1', ['this', Query('do2')])])),
    # subcommand multiword and multiarg tests
    ('[.do .do1 [this multi]]', Query('do', [Query('do1', ['this multi'])])),
    ('[.do .do1 [  this multi] [and] [this] .do2]', Query('do', [Query('do1', ['  this multi', 'and', 'this', Query('do2')])])),
    # random nested tests
    ('.do1 .do2 .do3 .do4', Query('do1', [Query('do2', [Query('do3', [Query('do4')])])])),
    ('[.do1 [.do2 [.do3 [.do4]]]]', Query('do1', [Query('do2', [Query('do3', [Query('do4')])])])),
    ('.do1 [multi arg] .do2 [word about] [.do3 .do4 another]', Query('do1', ['multi arg', Query('do2', ['word about', Query('do3', [Query('do4', ['another'])])])])), 
    # kwargs test
    ('.do usr=why', Query('do', kwargs={'usr' : 'why'})),
    ('.do usr=why chat=how', Query('do', kwargs={'usr' : 'why', 'chat' : 'how'})),
    ('.do [usr=why] chat=how', Query('do', kwargs={'usr' : 'why', 'chat' : 'how'})),
    ('[.do [usr=why] [chat=how]]', Query('do', kwargs={'usr' : 'why', 'chat' : 'how'})),
    ('.do [usr= why do we ]', Query('do', kwargs={'usr' : ' why do we '})),
    ('.do [usr= why do we ]', Query('do', kwargs={'usr' : ' why do we '})),
    # kwargs and args simultaneously
    ('.do be usr=why', Query('do', ['be'], {'usr' : 'why'})),
    ('.do be usr=why [how]', Query('do', ['be', 'how'], {'usr' : 'why'})),
    # subcommand kwargs
    # ('.do [usr=.do1]', Query('do', kwargs={'usr' : Query('do1')}))
    # ('.do usr=[.do1 and]', Query('do', kwargs={'usr' : Query('do1', ['and'])}))
    # ('.do usr=[.do1 or and=what]', Query('do', kwargs={'usr' : Query('do1', ['or'], {'and' : 'what'})}))
    # escapings
    ('.do [\.arg \] \[]', Query('do', ['\.arg \] \['])),
    # raw args
    ('.do r[.arg ] []r', Query('do', ['\.arg \] \['])),

] 

@pytest.mark.parametrize('input, result', qtest_data)
def test_query_from_str(input, result):
    assert Query.from_str(input) == result


@pytest.mark.parametrize('input',[
    '.do [1', '.do [1 [2', '.do r[1',
    '.do r[1]', '.do r[r[]]'
])
def test_query_command_syntax_error(input):
    with pytest.raises(CommandSyntaxError):
        Query.from_str(input)


