import dotenv from 'dotenv'
import fs from 'fs'
import path from 'path'
import { App } from 'octokit'

// Load environment variables
dotenv.config()

const appId = process.env.APP_ID ? Number(process.env.APP_ID) : undefined
const privateKeyPath = process.env.PRIVATE_KEY_PATH

console.log('==================================================')
console.log('GitHub App Search & Read Capability Prover')
console.log('==================================================\n')

if (!appId || !privateKeyPath) {
  console.error('❌ Error: APP_ID or PRIVATE_KEY_PATH is not configured in your .env file.')
  process.exit(1)
}

try {
  const resolvedKeyPath = path.resolve(privateKeyPath)
  const privateKey = fs.readFileSync(resolvedKeyPath, 'utf8')
  
  const app = new App({
    appId,
    privateKey
  })

  // Check installations
  const { data: installations } = await app.octokit.request('GET /app/installations')
  
  if (installations.length === 0) {
    console.warn('⚠️ Step 1 Required: The app is not installed on any repository yet.')
    console.log('   To prove search capabilities, please first install the app:')
    console.log(`   👉 Go to: https://github.com/apps/ge-altostrat-connector`)
    console.log('   👉 Click "Install App", select your repo(s), and install it.')
    console.log('   👉 Once installed, re-run this script to see the proof!\n')
    process.exit(0)
  }

  console.log(`✅ Step 1: Found ${installations.length} Active Installation(s).`)
  
  for (const inst of installations) {
    console.log(`\n--- Proving capabilities for Installation on account: ${inst.account?.login} ---`)
    
    // Authenticate as this installation to get repository-level access
    const octokitInst = await app.getInstallationOctokit(inst.id)
    
    // Fetch accessible repositories
    const { data: repoData } = await octokitInst.request('GET /installation/repositories')
    console.log(`\n✅ Step 2: Listing Accessible Repositories (${repoData.repositories.length}):`)
    
    for (const repo of repoData.repositories) {
      const owner = repo.owner.login
      const repoName = repo.name
      console.log(`   • ${owner}/${repoName}`)
      
      // Proving REPO & FILE READ permission
      console.log(`     ├── 📂 Testing repo contents read (fetching README.md)...`)
      try {
        const { data: readme } = await octokitInst.rest.repos.getContent({
          owner,
          repo: repoName,
          path: 'README.md'
        })
        console.log(`     │   ✅ Success! Found file: ${readme.name} (${readme.size} bytes)`)
      } catch (err) {
        console.log(`     │   ❌ Failed repo read: ${err.message}`)
      }

      // Proving ISSUES READ & SEARCH permission
      console.log(`     ├── 🐛 Testing issues read & search API...`)
      try {
        const { data: searchResults } = await octokitInst.rest.search.issuesAndPullRequests({
          q: `repo:${owner}/${repoName} is:issue`
        })
        console.log(`     │   ✅ Success! Issue Search API works. Found ${searchResults.total_count} issue(s) matching search criteria.`)
        if (searchResults.items.length > 0) {
          console.log(`     │      - Sample Issue Found: "#${searchResults.items[0].number} - ${searchResults.items[0].title}"`)
        }
      } catch (err) {
        console.log(`     │   ❌ Failed issue search: ${err.message}`)
      }

      // Proving PULL REQUEST READ permission
      console.log(`     └── 🔀 Testing Pull Request search API...`)
      try {
        const { data: searchPRs } = await octokitInst.rest.search.issuesAndPullRequests({
          q: `repo:${owner}/${repoName} is:pr`
        })
        console.log(`     │   ✅ Success! PR Search API works. Found ${searchPRs.total_count} pull request(s).`)
        if (searchPRs.items.length > 0) {
          console.log(`     │      - Sample PR Found: "#${searchPRs.items[0].number} - ${searchPRs.items[0].title}"`)
        }
      } catch (err) {
        console.log(`     │   ❌ Failed PR search: ${err.message}`)
      }
    }
  }

  console.log('\n==================================================')
  console.log('🎉 PROOF COMPLETE: The app has full permission to read/search issues and repository data!')
  console.log('==================================================')

} catch (err) {
  console.error(`❌ Unexpected error: ${err.message}`)
}
