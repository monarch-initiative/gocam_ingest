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
    model_data = row
    
    model_id = model_data.get('id')
    title = model_data.get('title', '')
    taxon = model_data.get('taxon', '')
    
    print(f"Processing model: {model_id}")
    print(f"Title: {title}")
    
    # Track all entities to avoid duplicates
    entities_written = set()
    
    # Process objects section for entity metadata
    objects_dict = {}
    if 'objects' in model_data:
        for obj in model_data['objects']:
            obj_id = obj.get('id')
            if obj_id:
                objects_dict[obj_id] = {
                    'label': obj.get('label', ''),
                    'type': obj.get('type', '')
                }
    
    # Process activities
    if 'activities' in model_data:
        for activity in model_data['activities']:
            activity_id = activity.get('id')
            if not activity_id:
                continue
                
            # Create activity node
            if activity_id not in entities_written:
                activity_entity = BiologicalProcessOrActivity(
                    id=activity_id,
                    name=f"Activity from {title}",
                    category=["biolink:BiologicalProcessOrActivity"]
                )
                koza_app.write(activity_entity)
                entities_written.add(activity_id)
            
            # Process enabled_by relationship
            if 'enabled_by' in activity:
                enabled_by = activity['enabled_by']
                gene_id = enabled_by.get('term')
                
                if gene_id:
                    # Create gene entity
                    if gene_id not in entities_written:
                        gene_label = objects_dict.get(gene_id, {}).get('label', gene_id)
                        gene_entity = Gene(
                            id=gene_id,
                            name=gene_label,
                            category=determine_node_category(gene_id)
                        )
                        koza_app.write(gene_entity)
                        entities_written.add(gene_id)
                    
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
                    if mf_term not in entities_written:
                        mf_label = objects_dict.get(mf_term, {}).get('label', mf_term)
                        mf_entity = MolecularActivity(
                            id=mf_term,
                            name=mf_label,
                            category=["biolink:MolecularActivity"]
                        )
                        koza_app.write(mf_entity)
                        entities_written.add(mf_term)
                    
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
    
    # Process any remaining objects not yet written
    for obj_id, obj_data in objects_dict.items():
        if obj_id not in entities_written:
            entity = Entity(
                id=obj_id,
                name=obj_data.get('label', obj_id),
                category=determine_node_category(obj_id, obj_data.get('type'))
            )
            koza_app.write(entity)
            entities_written.add(obj_id)
