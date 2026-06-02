import { execSync } from 'child_process'
import sys from 'os'

const PROJECT_ID = 'uk-bh-experiments-argolis'
const LOCATION = 'us'
const ENGINE_ID = 'ge-demo_1760707227647'

console.log('==================================================')
console.log('Gemini Enterprise (GE) Search Query Tool')
console.log('==================================================')

// Get the search query from command line args, default to 'Large objects'
const queryText = process.argv.slice(2).join(' ') || 'Large objects'
console.log(`🔍 Search Query: "${queryText}"\n`)

// 1. Get gcloud OAuth token
let token
try {
  token = execSync('gcloud auth print-access-token', { encoding: 'utf8' }).trim()
} catch (err) {
  console.error('❌ Failed to get access token from gcloud. Make sure you are logged in via: gcloud auth login')
  process.exit(1)
}

// 2. Query the serving config search endpoint
const domain = `${LOCATION}-discoveryengine.googleapis.com`
const url = `https://${domain}/v1/projects/${PROJECT_ID}/locations/${LOCATION}/collections/default_collection/engines/${ENGINE_ID}/servingConfigs/default_search:search`

const payload = {
  query: queryText,
  pageSize: 5
}

try {
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      'X-Goog-User-Project': PROJECT_ID
    },
    body: JSON.stringify(payload)
  })

  if (!res.ok) {
    const errorText = await res.text()
    console.error(`❌ API returned error status ${res.status}: ${errorText}\n`)
    process.exit(1)
  }

  const data = await res.json()
  
  if (!data.results || data.results.length === 0) {
    console.log('✨ No search results found matching this query in the GitHub connector data stores.')
    process.exit(0)
  }

  console.log(`🎉 Found ${data.results.length} Search Result(s):\n`)

  data.results.forEach((item, index) => {
    const doc = item.document
    const structData = doc.derivedStructData || {}
    
    console.log(`[Result ${index + 1}]`)
    console.log(`• ID:      ${doc.id}`)
    if (structData.title) console.log(`• Title:   ${structData.title}`)
    if (structData.link)  console.log(`• Link:    ${structData.link}`)
    
    // Extract snippet if present
    if (structData.snippets && structData.snippets.length > 0) {
      console.log(`• Snippet:`)
      structData.snippets.forEach(s => {
        console.log(`  > ${s.snippet.replace(/<\/?b>/g, '')}`) // strip <b> matching tags for cleaner console output
      });
    } else if (doc.structData) {
      // Fallback: dump structData key attributes nicely
      console.log(`• Attributes:`)
      const keys = ['state', 'body', 'description', 'message', 'file_path', 'author']
      keys.forEach(k => {
        if (doc.structData[k]) {
          const val = typeof doc.structData[k] === 'object' ? JSON.stringify(doc.structData[k]) : doc.structData[k]
          console.log(`  - ${k}: ${val.toString().substring(0, 120)}${val.toString().length > 120 ? '...' : ''}`)
        }
      })
    }
    console.log('--------------------------------------------------\n')
  })

} catch (err) {
  console.error(`❌ Error querying Gemini Enterprise: ${err.message}`)
}
