from utils.decorators import decorate


@decorate(retry=5)
def main(args):
    pass
