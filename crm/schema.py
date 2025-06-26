import graphene

# Dummy mutation class
class SayHello(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    message = graphene.String()

    def mutate(self, info, name):
        return SayHello(message=f"Hello, {name}!")

class Mutation(graphene.ObjectType):
    say_hello = SayHello.Field()

class Query(graphene.ObjectType):
    hello = graphene.String()

    def resolve_hello(root, info):
        return "Hello, GraphQL!"
