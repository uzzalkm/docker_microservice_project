from pathlib import Path
from ariadne import ScalarType, load_schema_from_path, make_executable_schema
from app.graphql.resolvers.customer import query
from app.graphql.resolvers.customerMutation import mutation
from app.graphql.resolvers.orderMutation import order_mutation

BASE_DIR = Path(__file__).resolve().parent

type_defs = load_schema_from_path(BASE_DIR / "schema.graphql")

long_scalar = ScalarType("Long")

@long_scalar.serializer
def serialize_long(value):
    return int(value)


@long_scalar.value_parser
def parse_long_value(value):
    return int(value)

schema = make_executable_schema(
type_defs,
query,
mutation,
order_mutation,
long_scalar
)