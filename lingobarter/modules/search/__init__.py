from ..accounts.models import User

# create 2dsphere index on User.Location
# we assume that location.type is Point
user_collection = User._get_collection()
user_collection.ensure_index(
    [('location.coordinates', '2dsphere')]
)

