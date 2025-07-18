import uuid

from biolink_model.datamodel.pydanticmodel_v2 import (
    Entity, 
    Gene, 
    BiologicalProcessOrActivity,
    MolecularActivity,
    Association
)
from koza.cli_utils import get_koza_app

koza_app = get_koza_app("Gene Ontology_GO causal activity models")

def extract_curie_prefix(curie: str) -> str:
    """Extract the prefix from a CURIE (e.g., 'GO' from 'GO:0003674')."""
    return curie.split(':')[0] if ':' in curie else ''

def determine_node_category(entity_id: str, entity_type: str = None) -> list:
    """Determine the biolink category for an entity based on its ID prefix."""
    prefix = extract_curie_prefix(entity_id)
    
    if prefix in ['ZFIN', 'MGI', 'RGD', 'SGD', 'FlyBase', 'WormBase', 'TAIR']:
        return ["biolink:Gene"]
    elif prefix == 'GO':
        if entity_type and 'molecular_function' in entity_type.lower():
            return ["biolink:MolecularActivity"]
        elif entity_type and 'biological_process' in entity_type.lower():
            return ["biolink:BiologicalProcess"]
        else:
            return ["biolink:OntologyClass"]
    elif prefix == 'ECO':
        return ["biolink:EvidenceType"]
    elif prefix == 'PMID':
        return ["biolink:Publication"]
    elif prefix == 'NCBITaxon':
        return ["biolink:OrganismTaxon"]
    elif 'gomodel:' in entity_id:
        return ["biolink:BiologicalProcessOrActivity"]
    else:
        return ["biolink:Entity"]

while (row := koza_app.get_row()) is not None:
    # Now each row is a single activity from the activities array
    activity = row
    
    activity_id = activity.get('id')
    if not activity_id:
        continue
    
    print(f"Processing activity: {activity_id}")
    
    # Create activity node
    activity_entity = BiologicalProcessOrActivity(
        id=activity_id,
        name=f"Activity {activity_id}",
        category=["biolink:BiologicalProcessOrActivity"]
    )
    koza_app.write(activity_entity)
    
    # Process enabled_by relationship
    if 'enabled_by' in activity:
        enabled_by = activity['enabled_by']
        gene_id = enabled_by.get('term')
        
        if gene_id:
            # Create gene entity
            gene_entity = Gene(
                id=gene_id,
                name=gene_id,  # We don't have access to objects dict with this approach
                category=determine_node_category(gene_id)
            )
            koza_app.write(gene_entity)
            
            # Create enabled_by association
            evidence_info = enabled_by.get('evidence', [{}])[0] if enabled_by.get('evidence') else {}
            
            enabled_by_assoc = Association(
                id=str(uuid.uuid4()),
                subject=activity_id,
                predicate="biolink:enabled_by",
                object=gene_id,
                category=["biolink:Association"],
                knowledge_level="knowledge_assertion",
                agent_type="manual_agent"
            )
            
            # Add evidence if present
            if evidence_info.get('term'):
                enabled_by_assoc.has_evidence = [evidence_info['term']]
            if evidence_info.get('reference'):
                enabled_by_assoc.publications = [evidence_info['reference']]
            
            koza_app.write(enabled_by_assoc)
    
    # Process molecular_function relationship
    if 'molecular_function' in activity:
        mf = activity['molecular_function']
        mf_term = mf.get('term')
        
        if mf_term:
            # Create molecular activity entity
            mf_entity = MolecularActivity(
                id=mf_term,
                name=mf_term,  # We don't have access to objects dict with this approach
                category=["biolink:MolecularActivity"]
            )
            koza_app.write(mf_entity)
            
            # Create molecular function association
            mf_assoc = Association(
                id=str(uuid.uuid4()),
                subject=activity_id,
                predicate="biolink:has_molecular_function",
                object=mf_term,
                category=["biolink:Association"],
                knowledge_level="knowledge_assertion",
                agent_type="manual_agent"
            )
            
            koza_app.write(mf_assoc)
