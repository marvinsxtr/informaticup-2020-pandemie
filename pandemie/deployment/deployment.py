import pandemie.web
from pandemie.tester.strategies import final


def deploy():
    """
    This function starts the Web-Service with the final-strategy
    """
    my_strategy = final.Final(silent=True)
    my_server = pandemie.web.WebServer(my_strategy, log="default")

    # Start server
    my_server.start()

    # Wait infinitely
    my_server.join()
