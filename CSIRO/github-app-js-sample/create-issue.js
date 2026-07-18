import dotenv from 'dotenv'
import fs from 'fs'
import path from 'path'
import { App } from 'octokit'

dotenv.config()

const appId = process.env.APP_ID ? Number(process.env.APP_ID) : undefined
const privateKeyPath = process.env.PRIVATE_KEY_PATH

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

  // Get active installations
  const { data: installations } = await app.octokit.request('GET /app/installations')
  
  if (installations.length === 0) {
    console.error('❌ Error: The app is not installed on any repository.')
    process.exit(1)
  }

  // Find the installation for brendanhills-altostrat
  const inst = installations.find(i => i.account?.login === 'brendanhills-altostrat')
  if (!inst) {
    console.error('❌ Error: No installation found for account "brendanhills-altostrat".')
    process.exit(1)
  }

  console.log(`🔑 Authenticating as installation ${inst.id} for account ${inst.account?.login}...`)
  const octokitInst = await app.getInstallationOctokit(inst.id)

  const owner = 'brendanhills-altostrat'
  const repo = 'ge_connector_demo'
  const title = 'Large objects'
  const body = 'This is an issue tracking the migration and management of large objects in our repository using Git LFS.'

  console.log(`🚀 Creating issue "${title}" in repository ${owner}/${repo}...`)
  
  const { data: issue } = await octokitInst.rest.issues.create({
    owner,
    repo,
    title,
    body
  })

  console.log(`✅ Success! Issue created successfully.`)
  console.log(`🔗 Link: ${issue.html_url}`)
  console.log(`🆔 Issue Number: #${issue.number}`)

} catch (err) {
  console.error(`❌ Failed to create issue: ${err.message}`)
}
