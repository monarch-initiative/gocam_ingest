"""
An example test file for the transform script.

It uses pytest fixtures to define the input data and the mock koza transform.
The test_example function then tests the output of the transform script.

See the Koza documentation for more information on testing transforms:
https://koza.monarchinitiative.org/Usage/testing/
"""

import pytest

from koza.utils.testing_utils import mock_koza

# Define the ingest name and transform script path
INGEST_NAME = "Gene Ontology_GO causal activity models"
TRANSFORM_SCRIPT = "./src/gocam_ingest/transform.py"


# Define an example row to test (as a dictionary)
@pytest.fixture
def example_row():
    return {
        "id": "gomodel:1234567",
        "title": "Test GOCAM Model",
        "taxon": "NCBITaxon:9606",
        "activities": [
            {
                "id": "gomodel:1234567/1",
                "enabled_by": {
                    "term": "MGI:1234567",
                    "evidence": [{"term": "ECO:0000314", "reference": "PMID:1234567"}]
                },
                "molecular_function": {
                    "term": "GO:0003674"
                }
            }
        ],
        "objects": [
            {
                "id": "MGI:1234567",
                "label": "entity_1",
                "type": "gene"
            },
            {
                "id": "GO:0003674",
                "label": "entity_6",
                "type": "molecular_function"
            }
        ]
    }


# Or a list of rows
@pytest.fixture
def example_list_of_rows():
    return [
        {
            "id": "gomodel:1234567",
            "title": "Test GOCAM Model 1",
            "taxon": "NCBITaxon:9606",
            "activities": [
                {
                    "id": "gomodel:1234567/1",
                    "enabled_by": {
                        "term": "MGI:1234567",
                        "evidence": [{"term": "ECO:0000314", "reference": "PMID:1234567"}]
                    },
                    "molecular_function": {
                        "term": "GO:0003674"
                    }
                }
            ],
            "objects": [
                {
                    "id": "MGI:1234567",
                    "label": "entity_1",
                    "type": "gene"
                },
                {
                    "id": "GO:0003674",
                    "label": "entity_6",
                    "type": "molecular_function"
                }
            ]
        },
        {
            "id": "gomodel:2345678",
            "title": "Test GOCAM Model 2",
            "taxon": "NCBITaxon:9606",
            "activities": [
                {
                    "id": "gomodel:2345678/1",
                    "enabled_by": {
                        "term": "MGI:2345678",
                        "evidence": [{"term": "ECO:0000314", "reference": "PMID:2345678"}]
                    },
                    "molecular_function": {
                        "term": "GO:0003675"
                    }
                }
            ],
            "objects": [
                {
                    "id": "MGI:2345678",
                    "label": "entity_2",
                    "type": "gene"
                },
                {
                    "id": "GO:0003675",
                    "label": "entity_7",
                    "type": "molecular_function"
                }
            ]
        },
    ]


# Define the mock koza transform
@pytest.fixture
def mock_transform(mock_koza, example_row):
    # Returns [entity_a, entity_b, association] for a single row
    return mock_koza(
        INGEST_NAME,
        example_row,
        TRANSFORM_SCRIPT,
    )


# Or for multiple rows
@pytest.fixture
def mock_transform_multiple_rows(mock_koza, example_list_of_rows):
    # Returns concatenated list of [entity_a, entity_b, association]
    # for each row in example_list_of_rows
    return mock_koza(
        INGEST_NAME,
        example_list_of_rows,
        TRANSFORM_SCRIPT,
    )


# Test the output of the transform


def test_single_row(mock_transform):
    # Should output: activity entity, gene entity, molecular function entity, 
    # enabled_by association, molecular_function association = 5 items
    assert len(mock_transform) == 5
    
    # Find the gene entity (should have name "entity_1")
    gene_entity = next((item for item in mock_transform 
                       if hasattr(item, 'name') and item.name == "entity_1"), None)
    assert gene_entity is not None
    assert gene_entity.id == "MGI:1234567"


def test_multiple_rows(mock_transform_multiple_rows):
    # Should output 5 items per model * 2 models = 10 items
    assert len(mock_transform_multiple_rows) == 10
    
    # Find entities with expected names
    entity_1 = next((item for item in mock_transform_multiple_rows 
                    if hasattr(item, 'name') and item.name == "entity_1"), None)
    entity_2 = next((item for item in mock_transform_multiple_rows 
                    if hasattr(item, 'name') and item.name == "entity_2"), None)
    
    assert entity_1 is not None
    assert entity_2 is not None
    assert entity_1.id == "MGI:1234567"
    assert entity_2.id == "MGI:2345678"
