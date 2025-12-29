# Automated Setup \[WIP\]

The aim is to automate or script the setup of the masterclass technical environment so that it can easily be replicated and also run by other people.

## Resources and Links

1. Terraform  
   1. [https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/discovery\_engine\_data\_store](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/discovery_engine_data_store)   
   2. [https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/vertex\_ai\_reasoning\_engine](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/vertex_ai_reasoning_engine)   
2. [https://github.com/GoogleCloudPlatform/cloud-foundation-fabric/tree/master/modules/agent-engine](https://github.com/GoogleCloudPlatform/cloud-foundation-fabric/tree/master/modules/agent-engine) 

## Tasks to Automate

1. Create Data Stores  
   1. Google Cloud Storage  
   2. Google Drive  
   3. Database?  
2. Create Gemini Enterprise Instance  
   1. Connect to data stores  
   2. Google Agents  
      1. Data Insights agent  
         1. BQ database setup  
         2. Connect DIA to BQ  
3. Configure Users Access to GE  
   1. Correct roles for agents etc  
   2. Added to project  
4. External user data (outside GE)  
   1. Google Calendar  
   2. Gmail  
   3. Google Drive   
5. User content in GE  
   1. NotebookLM  
   2. Run IdeaGeneration Agent	  
6. Custom agents  
   1. Financial Advisor  
   2. Others?

