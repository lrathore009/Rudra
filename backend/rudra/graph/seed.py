"""Seed entities for the Vikram / Rudra ecosystem."""

from rudra.graph.models import EntityType, GraphRelationType

SEED_ENTITIES: list[dict] = [
    {"name": "Vikram Rathore", "entity_type": EntityType.PERSON.value, "description": "Founder and operator of Rudra OS"},
    {"name": "Rudra OS", "entity_type": EntityType.PROJECT.value, "description": "Personal Intelligence Operating System"},
    {"name": "Jobsflix", "entity_type": EntityType.COMPANY.value, "description": "Jobsflix parent company"},
    {"name": "Jobsflix Nexus AI", "entity_type": EntityType.APP.value, "description": "Jobsflix AI platform"},
    {"name": "Jobsflix ATS", "entity_type": EntityType.APP.value, "description": "Applicant tracking system"},
    {"name": "HumanEdge", "entity_type": EntityType.PROJECT.value, "description": "HumanEdge initiative"},
    {"name": "AppHive Solutions", "entity_type": EntityType.COMPANY.value, "description": "AppHive Solutions"},
    {"name": "ChemSphere", "entity_type": EntityType.PROJECT.value, "description": "ChemSphere project"},
    {"name": "PhiloSphere", "entity_type": EntityType.PROJECT.value, "description": "PhiloSphere project"},
    {"name": "AstroSphere", "entity_type": EntityType.PROJECT.value, "description": "AstroSphere project"},
    {"name": "NeuroSphere", "entity_type": EntityType.PROJECT.value, "description": "NeuroSphere project"},
    {"name": "BioSphere", "entity_type": EntityType.PROJECT.value, "description": "BioSphere project"},
    {"name": "FutureForge Engineering", "entity_type": EntityType.COMPANY.value, "description": "FutureForge Engineering"},
    {"name": "Equation Universe", "entity_type": EntityType.PROJECT.value, "description": "Equation Universe project"},
]

SEED_RELATIONSHIPS: list[tuple[str, str, str]] = [
    ("Vikram Rathore", "Rudra OS", GraphRelationType.OWNS.value),
    ("Vikram Rathore", "Jobsflix", GraphRelationType.OWNS.value),
    ("Jobsflix", "Jobsflix Nexus AI", GraphRelationType.OWNS.value),
    ("Jobsflix", "Jobsflix ATS", GraphRelationType.OWNS.value),
    ("Vikram Rathore", "HumanEdge", GraphRelationType.WORKS_ON.value),
    ("Vikram Rathore", "ChemSphere", GraphRelationType.WORKS_ON.value),
    ("Vikram Rathore", "PhiloSphere", GraphRelationType.WORKS_ON.value),
    ("Vikram Rathore", "AstroSphere", GraphRelationType.WORKS_ON.value),
    ("Vikram Rathore", "NeuroSphere", GraphRelationType.WORKS_ON.value),
    ("Vikram Rathore", "BioSphere", GraphRelationType.WORKS_ON.value),
    ("AppHive Solutions", "FutureForge Engineering", GraphRelationType.RELATED_TO.value),
    ("Rudra OS", "Jobsflix Nexus AI", GraphRelationType.RELATED_TO.value),
]
