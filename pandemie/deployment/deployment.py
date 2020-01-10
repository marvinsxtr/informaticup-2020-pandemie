import pandemie.web
from pandemie.tester.strategies import final


def deploy():
    my_strategy = final.Final()
    my_server = pandemie.web.WebServer(my_strategy, log="default")

    # Start server
    my_server.start()

    # Wait infinitely
    my_server.join()
