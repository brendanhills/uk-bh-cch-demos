**PRD Title: Catalyst Lab “Front Door” AI Agent** 

**Author: Ben Morgan** 

**Team:** Catalyst Lab 

**Product Manager:** Ben Morgan 

**Engineering Lead/Team Lead:** Kris Wilkinson, Vahe & Ravi from SalesForce, Remya  Panikar, Ashish Chauhan 

**Status of PRD:** In development 

**Executive Summary** 

The Catalyst Lab “Front Door” AI Agent is a digital entry point for capturing, ideating and  processing a wide range of business inputs across Capita. It replaces static submission forms  with a conversational interface, allowing users to submit requests naturally via chat or voice. 

This agent is designed to support all types of inbound requests to Catalyst Lab, including: • **Innovation ideas** – new concepts or improvements from across the business. • **Customer requests** – opportunities or needs identified through client interactions. • **Internal build requests** – suggestions for propositions, tools, processes, or capabilities  to be developed internally. 

• **Pre-sales engagements** – early-stage solutioning and ideation to support business  development. 

The agent must be capable of recognising the type of request and taking the appropriate action  based on its intent and need. 

Crucially, the agent is not just a collection tool — its core function is to answer the “why”  behind every submission. Before any request reaches a human reviewer, the agent will clarify  the rationale, assess the potential business impact, and determine strategic alignment. This  ensures that every submission is contextualised, prioritised, and actionable, significantly  reducing manual triage and accelerating decision-making. 

**Key Features** 

• **Conversational AI** 

Natural language chat and voice interface that enables users to submit requests  intuitively. The agent acts as a virtual consultant, guiding users through the process of  exploring, refining, and stress-testing their ideas before formal submission. It  encourages deeper thinking and helps shape raw concepts into actionable proposals. It  picks up context during the conversation to provide a dynamic conversational user  experience. 

• **Intelligent Triage** 

Clarifies the purpose behind each request, assesses business impact, detects 

Confidential External \- Data to be shared with caution.   
duplicates, and determines the appropriate next step. It ensures every submission is  grounded in a clear “why” and is ready for meaningful evaluation. 

• **Automated Research** 

Benchmarks submissions against internal and external data sources, surfacing relevant  insights, comparable solutions, and strategic context. This supports users in validating  and evolving their ideas during the conversation. 

• **Press Release / FAQ Generator** 

Transforms ideas into clear, compelling summaries that articulate the business case  and strategic value helping users communicate effectively with stakeholders and  decision-makers. 

• **Salesforce Native** 

Fully integrated with AgentForce and Catalyst Lab workflows, enabling seamless  handoff, tracking, and visibility across the innovation lifecycle. 

• **Structured Output** 

Captures submissions in a structured format, allowing Catalyst Lab to filter, assess,  and prioritise inputs at scale. Even exploratory or early-stage ideas are recorded in a  way that supports rigorous evaluation. 

• **Status updates** 

Allows for users to request an update of their previous requests if they provide the correct refence number. The agent uses the Request Log to provide sanitized updates  using the Status field and the Phase. 

**Strategic Value** 

• Supports a broader range of business inputs beyond innovation alone. • Ensures that the “why” behind the request is answered allowing for the core reason  behind the request is defined before human review. 

• Ensures the requestor understands and articulates that the request is either increasing  revenue, reducing costs of increasing brand value for Capita. It should also disqualify  any requests that do not clearly address one of these points.  

• Improves the quality and completeness of submissions, including business impact  analysis. 

• Reduces manual triage workload for Catalyst Lab teams. 

• Enhances visibility, traceability, and consistency in how requests are handled. 

**Overview** 

The Catalyst Lab “Front Door” AI Agent is designed to capture and process a wide range of  business inputs through a conversational interface. It operates as follows: 

**1\. Input Capture via Natural Language** 

Users initiate a submission using chat or voice. The agent supports four primary request types: • Innovation ideas

Confidential External \- Data to be shared with caution.   
• Customer requests 

• Internal build requests 

• Pre-sales engagements 

**2\. Dynamic Dialogue and Context Gathering** 

The agent engages the user in a guided conversation to: 

• Clarify the intent of the request 

• Gather relevant context (e.g. business area, urgency, dependencies) • Estimate potential business impact and cost implications. The agent asks probing  questions that  

• Understanding the tools, stakeholders, clients and data sources 

• Flesh out and refine ideas through dynamic dialogue, acting as a virtual consultant to  help users explore possibilities, challenge assumptions, and strengthen the business  case before submission 

**3\. Intelligent Triage** 

Using AI-based classification, the agent: 

• Identifies the type of request 

• Detects duplicates or similar past submissions. Surfaces similar ideas and their original  business users to the user, enabling them to build on existing work or connect directly  with the idea owner. 

• Checks internal product lists for potential, pre-built solutions to the request. It should  ask the user if an existing solution (“one we’ve built earlier”) fits their needs, offering a  link to the relevant product or submission for review. 

• Checks internal Catalyst Lab scope list. This enables the agent to know which Catalyst  Lab member to assign to the request as it is dependent on scope of work. 

**4\. Automated Research** 

The agent performs background analysis by: 

• Referencing previous Catalyst Lab submissions 

• Reviewing external market trends and comparable technologies 

• Estimating business impact and cost based on available data 

**5\. PR/FAQ Style Summary Generation** 

Based on the gathered information, the agent: 

• Generates a concise, structured summary of the request with a detailed FAQ. The  summary should use data from the conversation plus contextual web search. The FAQs  should be relevant to the request and not the same every time.  

• Presents the summary to the user for review and refinement 

• Ensures clarity and alignment before final submission

Confidential External \- Data to be shared with caution.   
**6\. Requestor Review and Refinement Loop** 

The generated summary is generated in a PDF format and sent to the requestor through the  chat interface for review. The requestor can: 

1\. **Approve** the summary if it accurately reflects their intent by stating that they approve in  the chat.  

2\. **Suggest amendments** if the summary is inaccurate or incomplete. They would do this  in a response to the agent in the chat.  

If amendments are requested: 

• The agent initiates a second conversational interaction to understand what needs to be  changed. 

• It asks targeted, contextual questions to refine its understanding. 

• The agent then re-runs the research and analysis steps to generate an updated  summary. 

• This revised version is returned to the requestor for final approval. 

**7\. Structured Submission and Handoff** 

Once finalised: 

• The agent parses the submission into a structured format 

• Stores it in the Catalyst Lab SalesForce database with automated and consistent  tagging of the request related to customer/contract, business sector (CE, CPS, Group)  or solution category (translation agent, knowledge agent, etc). 

• Enables visibility and traceability across the innovation lifecycle. 

• Notifies the Catalyst Lab that a new request has been added to the SalesForce  database.  

**Problem** 

Business users often struggle to articulate innovation ideas clearly or they are incomplete.  Static forms fail to capture nuanced context, leading to misaligned expectations and inefficient  evaluation. There is no scalable way to triage, research, and refine these requests  collaboratively. 

**Objectives** 

• Enable natural language submission of innovation requests via chat or voice • Use AI to ask clarifying questions and uncover true intent 

• Conduct deep research on innovation requests, including comparing previous requests,  external tooling comparisons, and cost and business impact analysis. 

• Generate a draft Press Release / FAQ style document (see Amazon’s PR/FAQ template) summarizing the request 

• Allow iterative refinement of the request and press release through continued conversation with the requestor 

• Support Catalyst Lab team in evaluating and prioritizing submissions

Confidential External \- Data to be shared with caution.   
**Constraints** 

• Must support secure handling of sensitive business data 

• Must operate within defined cost and token usage limits 

**Persona** 

**Key Persona**: Business User submitting requests via Front Door agent **Persona 2**: Catalyst Lab Team Member evaluating and triaging submissions 

**Features in scope** 

**Conversational Interface** 

• Chat and voice support (via AgentForce) 

• Context-aware dialogue flow 

**Dynamic Questioning** 

• AI-generated qualifying questions 

• Adaptive follow-ups based on user responses 

• The agent should use web search to ask the requestor questions that help refine the  request 

**Research & Analysis** 

• Internal submission comparison (duplicate detection) 

• External market and tooling analysis 

• Cost and business impact estimation 

• Identification of related business units 

**Press Release Generation** 

• Drafting of a concise, compelling summary 

• Iterative refinement via voice or chat 

**Integration** 

• Native Salesforce CRM integration 

• Catalyst Lab dashboard integration (backlog items are being moved to SalesForce so  integration may not be necessary) 

• PowerBI integration 

• Email integration 

• Microsoft Teams integration 

**Data Handling** 

• Secure storage of submissions 

• Metadata tagging and versioning 

• Attachment support for the PRFAQ PDF

Confidential External \- Data to be shared with caution.   
• Activity log to understand when a field or status has changed.  

• Automated status field updates following comments or field changes.  **Feedback Loop** 

• User feedback on press release quality 

• Catalyst Lab feedback on submission clarity 

**Business User Journey** 

1\. **Initiate Request**: Opens chat or voice interface via Catalyst Lab idea intake UI. 2\. **Input personal information**: Input name and email address. 

3\. **Conversational Intake**: AI asks clarifying questions to understand the idea. 4\. **Draft Summary**: AI generates a press release-style summary based on the deep  research conducted on market impact, external tooling comparison and cost analysis. 5\. **Refinement Loop**: User iteratively improves the summary via conversation. 6\. **Submission**: Finalized request is submitted to Catalyst Lab. 

**Catalyst Lab Team Journey** 

1\. **Review Dashboard**: Accesses submissions via Catalyst Lab dashboard. 2\. **Evaluate Submission**: Reviews summary, metadata, and impact analysis. 3\. **Provide Feedback**: Adds comments or requests clarification. 

4\. **Field Updates**: Enabled to update fields where necessary.  

5\. **Prioritize**: Tags and triages for further exploration or development. 

6\. **Project Management**: Moves the requests through the project stages.  7\. **Notification:** Notified when a new request is added by a business user. 

**Data storage & access** 

• Primary Storage: Salesforce CRM 

o Stored Data Includes: 

▪ Submission summary 

▪ Key request metadata (e.g., business unit, impact area, urgency,  

requestor info) 

▪ Attachment of latest draft press release 

▪ Submission status and history 

**Salesforce Integration & Request Lifecycle Management**

Confidential External \- Data to be shared with caution.   
The Catalyst Lab “Front Door” AI Agent will feed into a dedicated, structured Salesforce  database designed specifically for Front Door submissions. Each validated request will  automatically generate a new record in this database, following a consistent schema that  includes: 

• Request title and description 

• Submission and required dates 

• Request type and client 

• Assigned business owner 

• ROI and strategic impact 

• Current stage in the lifecycle 

• PDF attachment of the PR/FAQ document 

Upon submission, the agent will send a notification to both the requestor and the Catalyst Lab.  The business user will receive a notification via email. The Catalyst Lab should receive their  notification via Microsoft Teams. This notification will include a summary of the request and a  direct link to the Salesforce record. 

**Product Owner Assignment** 

The agent will automatically assign a business owner based on the client or proposition area,  using a ruleset (to be created). For example: 

• GIS or Smart Buildings → Aaron 

• Training or Enablement → Alexandra Stewart 

• Data → Rachel Brooks 

• Sean Kershaw → Contact Centres 

• Knowledge Bases → Tom Willetts 

• If there is no clear owner, then the request should default to Ben Morgan This ensures that requests are routed to the most relevant owner for review and progression. **Lifecycle Tracking** 

Each request should be assigned initially to the “Idea” stage, which can be updated as the  request moves through the innovation lifecycle (e.g., Discovery → MVP → Pilot → Scale). Stage  updates can be made by the Catalyst Lab team or the assigned owner, ensuring visibility and  traceability throughout. 

If the agent recognizes that the business user is speaking about a bid that Capita is working on,  then it should assign the request to the Bid phase instead of the Idea phase. 

Confidential External \- Data to be shared with caution.   
**Success Metrics** 

• Duplicate request detection accuracy: \> 90% 

• Press release approval rate: \> 80% 

• Average time to complete submission, \< 10 minutes 

• User satisfaction (CSAT), \> 85% 

• Submission-to-review cycle time, \< 3 business days 

• Request completeness rate \>90% 

**Access Control**

| Role  | Access Level  | Description |
| :---- | :---- | :---- |
| Business User  | Submit & View Own  | Can submit requests via the chat  interface. Can request status   updates for their request via the chat  interface. |
| Catalyst Lab Team  | Full Access  | Can view, edit, triage, and prioritize  all submissions via the SalesForce  database |
| Admin  | Admin Access  | Manage system settings, user roles,  and integrations |

Confidential External \- Data to be shared with caution. 