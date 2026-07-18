import { execSync } from 'child_process'

const PROJECT_ID = 'uk-bh-experiments-argolis'
const LOCATION = 'us'

// ANSI Escape Codes for premium terminal styling
const RESET = '\x1b[0m'
const BOLD = '\x1b[1m'
const GREEN = '\x1b[32m'
const RED = '\x1b[31m'
const YELLOW = '\x1b[33m'
const CYAN = '\x1b[36m'
const MAGENTA = '\x1b[35m'
const WHITE = '\x1b[37m'
const BG_RED = '\x1b[41m'

console.log(`${BOLD}${CYAN}==================================================${RESET}`)
console.log(`${BOLD}${CYAN}   Gemini Enterprise (GE) Data Connector Monitor   ${RESET}`)
console.log(`${BOLD}${CYAN}==================================================${RESET}\n`)

// 1. Get gcloud OAuth token
let token
try {
  console.log(`🔑 ${BOLD}Fetching gcloud access token...${RESET}`)
  token = execSync('gcloud auth print-access-token', { encoding: 'utf8' }).trim()
  console.log(`✅ ${GREEN}Access token obtained successfully.${RESET}\n`)
} catch (err) {
  console.error(`❌ ${RED}Failed to get access token from gcloud. Make sure you are logged in via: gcloud auth login${RESET}`)
  process.exit(1)
}

// 2. Fetch all collections in us location to discover the GitHub Connector dynamically
const listCollectionsUrl = `https://us-discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/${LOCATION}/collections`
console.log(`📡 ${BOLD}Scanning active collections in location "${LOCATION}"...${RESET}`)

try {
  const collectionsRes = await fetch(listCollectionsUrl, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      'X-Goog-User-Project': PROJECT_ID
    }
  })

  if (!collectionsRes.ok) {
    const errText = await collectionsRes.text()
    console.error(`❌ ${RED}Failed to list collections (Status ${collectionsRes.status}): ${errText}${RESET}`)
    process.exit(1)
  }

  const collectionsData = await collectionsRes.json()
  const collections = collectionsData.collections || []

  // Find the GitHub Connector collection
  const githubCollection = collections.find(c => c.dataConnector && c.dataConnector.dataSource === 'github')

  if (!githubCollection) {
    console.log(`⚠️ ${YELLOW}No active GitHub data connector collection found in your GCP project.${RESET}`)
    process.exit(0)
  }

  const collectionId = githubCollection.name.split('/').pop()
  const dc = githubCollection.dataConnector

  console.log(`\n${BOLD}${GREEN}⚡ FOUND GITHUB DATA CONNECTOR${RESET}`)
  console.log(`   • ${BOLD}Collection Name:${RESET}  ${collectionId}`)
  console.log(`   • ${BOLD}Display Name:${RESET}     ${githubCollection.displayName}`)
  console.log(`   • ${BOLD}Connector State:${RESET}  ${dc.state === 'ACTIVE' ? `${GREEN}${BOLD}ACTIVE${RESET}` : `${YELLOW}${dc.state}${RESET}`}`)
  console.log(`   • ${BOLD}Connector Type:${RESET}   ${dc.connectorType}`)
  console.log(`   • ${BOLD}Created Time:${RESET}     ${dc.createTime || 'N/A'}`)
  console.log(`   • ${BOLD}Last Updated:${RESET}     ${dc.updateTime || 'N/A'}`)

  if (dc.actionConfig && dc.actionConfig.actionParams) {
    console.log(`\n   ${BOLD}--- Action Config Parameters ---${RESET}`)
    const params = dc.actionConfig.actionParams
    console.log(`   • ${BOLD}Owner Login:${RESET}      ${CYAN}${params.owner_login}${RESET}`)
    console.log(`   • ${BOLD}Auth Type:${RESET}        ${CYAN}${params.auth_type}${RESET}`)
  }

  // 3. Scan GCP Cloud Logging for recent Authorization issues
  console.log(`\n🔍 ${BOLD}Analyzing GCP Logging for data connector health...${RESET}`)
  try {
    const filter = `resource.type="audited_resource" AND protoPayload.serviceName="discoveryengine.googleapis.com" AND protoPayload.methodName="google.cloud.discoveryengine.v1main.DataConnectorService.AcquireAccessToken"`
    const logCommand = `gcloud logging read "${filter}" --limit=10 --format="json(timestamp, protoPayload.status)"`
    const logsRaw = execSync(logCommand, { encoding: 'utf8' }).trim()
    
    if (logsRaw && logsRaw !== '[]') {
      const logs = JSON.parse(logsRaw)
      const authErrors = logs.filter(log => log.protoPayload && log.protoPayload.status && log.protoPayload.status.message)
      
      if (authErrors.length > 0) {
        const latestErr = authErrors[0].protoPayload.status.message
        console.log(`\n${BG_RED}${BOLD}${WHITE}  ⚠️  CRITICAL DIAGNOSTIC ALERT  ${RESET}`)
        console.log(`${RED}${BOLD}🚨 Google Cloud is currently unable to authenticate with GitHub using this connector!${RESET}`)
        console.log(`${YELLOW}Reason reported by Discovery Engine API:${RESET}`)
        console.log(`   "${latestErr}"`)
        console.log(`\n${BOLD}💡 HOW TO RESOLVE THIS ISSUE:${RESET}`)
        console.log(`   1. Go to your Google Cloud Console for project: ${BOLD}${PROJECT_ID}${RESET}`)
        console.log(`   2. Navigate to ${BOLD}Vertex AI Agent Builder > Data Stores${RESET}`)
        console.log(`   3. Select the Data Store associated with this connector.`)
        console.log(`   4. Click the ${BOLD}"Log In"${RESET} or ${BOLD}"Re-authorize"${RESET} button to complete the GitHub App handshake.`)
        console.log(`      (This is required because correcting the "owner_login" parameter invalidated the previous OAuth link).`)
      } else {
        console.log(`✅ ${GREEN}No connection or authorization errors found in the last 10 logs.${RESET}`)
      }
    } else {
      console.log(`✅ ${GREEN}No connection or authorization errors found in the logs.${RESET}`)
    }
  } catch (logErr) {
    console.log(`⚠️ ${YELLOW}Unable to check GCP logs for health status: ${logErr.message}${RESET}`)
  }

  // 4. Check status of individual data stores (entities)
  console.log(`\n📋 ${BOLD}Data Store Ingestion Details:${RESET}`)
  console.log(`${CYAN}--------------------------------------------------${RESET}`)

  const entities = dc.entities || []
  for (const entity of entities) {
    const dsId = entity.dataStore.split('/').pop()
    const dsUrl = `https://us-discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/${LOCATION}/collections/default_collection/dataStores/${dsId}`

    try {
      const dsRes = await fetch(dsUrl, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-Goog-User-Project': PROJECT_ID
        }
      })

      if (dsRes.ok) {
        const dsData = await dsRes.json()
        console.log(`🔹 ${BOLD}Entity type:${RESET}     ${CYAN}${entity.entityName.toUpperCase()}${RESET}`)
        console.log(`   • ${BOLD}Data Store ID:${RESET}   ${dsId}`)
        console.log(`   • ${BOLD}Display Name:${RESET}    ${dsData.displayName}`)
        
        // Query branch 0/documents
        const docsUrl = `https://us-discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/${LOCATION}/collections/default_collection/dataStores/${dsId}/branches/0/documents?pageSize=1`
        const docsRes = await fetch(docsUrl, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'X-Goog-User-Project': PROJECT_ID
          }
        })

        if (docsRes.ok) {
          const docsData = await docsRes.json()
          const hasDocs = docsData.documents && docsData.documents.length > 0
          if (dc.connectorModes && dc.connectorModes.includes('FEDERATED')) {
            console.log(`   • ${BOLD}Ingestion State:${RESET} ${GREEN}🎉 SYNCHRONIZED (FEDERATED MODE)${RESET}`)
            console.log(`                    (Documents are queried directly from GitHub in real-time)`)
          } else {
            console.log(`   • ${BOLD}Ingestion State:${RESET} ${hasDocs ? `${GREEN}🎉 INGESTED & ACTIVE (${docsData.documents.length} docs found)${RESET}` : `${YELLOW}⏳ Synced but empty${RESET}`}`)
          }
        } else {
          console.log(`   • ${BOLD}Ingestion State:${RESET} ${YELLOW}⏳ Pending initial synchronization (Uninitialized branch)${RESET}`)
        }
      } else {
        console.log(`🔹 ${BOLD}Entity type:${RESET}     ${CYAN}${entity.entityName.toUpperCase()}${RESET}`)
        console.log(`   ❌ ${RED}Failed to query data store details for ID ${dsId}: Status ${dsRes.status}${RESET}`)
      }
    } catch (dsErr) {
      console.log(`🔹 ${BOLD}Entity type:${RESET}     ${CYAN}${entity.entityName.toUpperCase()}${RESET}`)
      console.log(`   ❌ ${RED}Network error fetching data store: ${dsErr.message}${RESET}`)
    }
    console.log(`${CYAN}--------------------------------------------------${RESET}`)
  }

} catch (err) {
  console.error(`❌ ${RED}Unexpected monitor error: ${err.message}${RESET}`)
}

console.log(`\n${BOLD}${CYAN}==================================================${RESET}`)
console.log(`${BOLD}${CYAN}   Monitor Run Complete                           ${RESET}`)
console.log(`${BOLD}${CYAN}==================================================${RESET}`)
