import os
import random

from pymilvus import (
    connections,
    FieldSchema, CollectionSchema, DataType,
    Collection,
    utility
)

from wasmer import (
    Store,
    Module,
    Instance
)

# This example shows how to:
#   1. connect to Milvus server
#   2. create function
#   3. run function
#   4. drop function
#   5. search


_HOST = '127.0.0.1'
_PORT = '19530'

# Const names
_COLLECTION_NAME = 'demo'
_ID_FIELD_NAME = 'id_field'
_VECTOR_FIELD_NAME = 'float_vector_field'

# Vector parameters
_DIM = 128
_INDEX_FILE_SIZE = 32  # max file size of stored index

# Index parameters
_METRIC_TYPE = 'L2'
_INDEX_TYPE = 'IVF_FLAT'
_NLIST = 1024
_NPROBE = 16
_TOPK = 3


# Create a Milvus connection
def create_connection():
    print(f"\nCreate connection...")
    connections.connect(host=_HOST, port=_PORT)
    print(f"\nList connections:")
    print(connections.list_connections())


# Create a collection named 'demo'
def create_collection(name, id_field, vector_field):
    field1 = FieldSchema(name=id_field, dtype=DataType.INT64, description="int64", is_primary=True)
    field2 = FieldSchema(name=vector_field, dtype=DataType.FLOAT_VECTOR, description="float vector", dim=_DIM,
                         is_primary=False)
    schema = CollectionSchema(fields=[field1, field2], description="collection description")
    collection = Collection(name=name, data=None, schema=schema)
    print("\ncollection created:", name)
    return collection


def has_collection(name):
    return utility.has_collection(name)


# Drop a collection in Milvus
def drop_collection(name):
    collection = Collection(name)
    collection.drop()
    print("\nDrop collection: {}".format(name))


# List all collections in Milvus
def list_collections():
    print("\nlist collections:")
    print(utility.list_collections())


def insert(collection, num, dim):
    data = [
        [i for i in range(num)],
        [[random.random() for _ in range(dim)] for _ in range(num)],
    ]
    collection.insert(data)
    return data[1]


def get_entity_num(collection):
    print("\nThe number of entity:")
    print(collection.num_entities)


def create_index(collection, filed_name):
    index_param = {
        "index_type": _INDEX_TYPE,
        "params": {"nlist": _NLIST},
        "metric_type": _METRIC_TYPE}
    collection.create_index(filed_name, index_param)
    print("\nCreated index:\n{}".format(collection.index().params))


def drop_index(collection):
    collection.drop_index()
    print("\nDrop index sucessfully")


def load_collection(collection):
    collection.load()


def release_collection(collection):
    collection.release()


def search(collection, vector_field, id_field, search_vectors):
    search_param = {
        "data": search_vectors,
        "anns_field": vector_field,
        "param": {"metric_type": _METRIC_TYPE, "params": {"nprobe": _NPROBE}},
        "limit": _TOPK,
        "expr": "id_field > 0"}
    results = collection.search(**search_param)
    for i, result in enumerate(results):
        print("\nSearch result for {}th vector: ".format(i))
        for j, res in enumerate(result):
            print("Top {}: {}".format(j, res))


def create_function(function_name, wasm_binary_file):
    # module = Module(Store(), wasm_binary_file)
    # instance = Instance(module)
    # result = instance.exports.sum(1, 2)
    # print(result)  # 3!
    utility.create_function(function_name, wasm_binary_file)


def drop_function(name):
    return utility.drop_function(name)



def main():
    # create a connection
    create_connection()

    # drop collection if the collection exists
    if has_collection(_COLLECTION_NAME):
        drop_collection(_COLLECTION_NAME)

    # create collection
    collection = create_collection(_COLLECTION_NAME, _ID_FIELD_NAME, _VECTOR_FIELD_NAME)

    __dir__ = os.path.dirname(os.path.realpath(__file__))

    print(__dir__)

    create_function('simple', open(__dir__ + '/simple.wasm', 'rb').read())

    drop_function('simple')
    # release memory
    release_collection(collection)

    # drop collection
    drop_collection(_COLLECTION_NAME)


if __name__ == '__main__':
    main()