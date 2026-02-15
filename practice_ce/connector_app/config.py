# Google Cloud Configuration
PROJECT_ID = "uk-bh-experiments-argolis"
LOCATION = "us"  # Explicitly requested by user

# Data Store Configuration
# The ID you want to assign to your new Data Store
DATA_STORE_ID = "cebank-compliance-store-v4"

# Human-readable name for the Data Store
DATA_STORE_DISPLAY_NAME = "CEBank Compliance Data"

# Identity Mapping Configuration (Advanced)
# If you are using identity mapping, provide the resource name here.
# Leave None if not using, or if you want to create a new one.
# Format: "projects/{project}/locations/{location}/identityMappingStores/{store_id}"
IDENTITY_MAPPING_STORE = None 

# Engine Configuration
# The ID of the App/Engine to link the Data Store to
ENGINE_ID = "agents-agentspace_1749039293552"