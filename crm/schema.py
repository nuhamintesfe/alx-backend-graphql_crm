import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.db import transaction
from django.core.exceptions import ValidationError
import re
from datetime import datetime

# Dummy mutation class
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
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
def validate_phone(phone):
    if phone:
        phone_pattern = re.compile(r"^\+?\d{1,3}[- ]?\d{3}[- ]?\d{3,4}$")
        if not phone_pattern.match(phone):
            raise ValidationError("Phone number format is invalid.")
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists.")
        try:
            validate_phone(phone)
        except ValidationError as e:
            raise Exception(str(e))

        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully.")
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created_customers = []
        errors = []

        for idx, cust_input in enumerate(input):
            try:
                # Check email uniqueness per customer
                if Customer.objects.filter(email=cust_input.email).exists():
                    raise Exception(f"Email '{cust_input.email}' already exists.")
                # Validate phone if provided
                if cust_input.phone:
                    validate_phone(cust_input.phone)

                # Create and save customer
                customer = Customer(
                    name=cust_input.name,
                    email=cust_input.email,
                    phone=cust_input.phone
                )
                customer.save()
                created_customers.append(customer)
            except Exception as e:
                errors.append(f"Error for customer at index {idx}: {str(e)}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)
class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise Exception("Price must be positive.")
        if stock < 0:
            raise Exception("Stock cannot be negative.")

        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)
class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime(required=False)

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        if not product_ids:
            raise Exception("At least one product must be selected.")

        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Customer does not exist.")

        products = Product.objects.filter(pk__in=product_ids)
        if products.count() != len(product_ids):
            raise Exception("One or more product IDs are invalid.")

        total_amount = sum([p.price for p in products])

        if not order_date:
            order_date = datetime.now()

        order = Order(customer=customer, order_date=order_date, total_amount=total_amount)
        order.save()
        order.products.set(products)
        order.save()
        return CreateOrder(order=order)
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
