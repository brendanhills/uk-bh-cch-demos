import dotenv from 'dotenv'
import fs from 'fs'
import path from 'path'
import { App } from 'octokit'

// Load environment variables
dotenv.config()

const appId = process.env.APP_ID ? Number(process.env.APP_ID) : undefined
const privateKeyPath = process.env.PRIVATE_KEY_PATH
const clientId = process.env.CLIENT_ID
const clientSecret = process.env.CLIENT_SECRET

console.log('==================================================')
console.log('GitHub App Credentials Diagnostic Tool')
console.log('==================================================\n')

// 1. Verify environment variables
let validEnv = true
if (!appId) {
  console.error('❌ Error: APP_ID is not set in .env')
  validEnv = false
} else if (appId === 11) {
  console.warn('⚠️ Warning: APP_ID is set to "11", which is likely a placeholder. Please ensure this matches your actual GitHub App ID.')
} else {
  console.log(`✅ APP_ID is set: ${appId}`)
}

if (!privateKeyPath) {
  console.error('❌ Error: PRIVATE_KEY_PATH is not set in .env')
  validEnv = false
} else {
  // Check if private key file exists
  try {
    const resolvedPath = path.resolve(privateKeyPath)
    if (!fs.existsSync(resolvedPath)) {
      console.error(`❌ Error: Private key file does not exist at path: ${resolvedPath}`)
      validEnv = false
    } else {
      const keyContent = fs.readFileSync(resolvedPath, 'utf8')
      if (!keyContent.includes('BEGIN RSA PRIVATE KEY') && !keyContent.includes('BEGIN PRIVATE KEY')) {
        console.error(`❌ Error: The file at ${resolvedPath} does not appear to be a valid PEM private key.`)
        validEnv = false
      } else {
        console.log(`✅ Private key file found and readable: ${resolvedPath}`)
      }
    }
  } catch (err) {
    console.error(`❌ Error reading private key file: ${err.message}`)
    validEnv = false
  }
}

if (!clientId) {
  console.warn('⚠️ Warning: CLIENT_ID is not set in .env. Note: Google Cloud Gemini Enterprise Data Connector requires Client ID for OAuth.')
} else {
  console.log(`✅ CLIENT_ID is set: ${clientId}`)
}

if (!clientSecret) {
  console.warn('⚠️ Warning: CLIENT_SECRET is not set in .env. Note: Google Cloud Gemini Enterprise Data Connector requires Client Secret for OAuth.')
} else {
  console.log(`✅ CLIENT_SECRET is set: (configured)`)
}

if (!validEnv) {
  console.error('\n❌ Environmental checks failed. Please fix your .env file before running again.')
  process.exit(1)
}

// 2. Attempt Authentication as GitHub App
console.log('\n--- Authenticating as GitHub App ---')
try {
  const resolvedKeyPath = path.resolve(privateKeyPath)
  const privateKey = fs.readFileSync(resolvedKeyPath, 'utf8')
  
  const app = new App({
    appId,
    privateKey
  })

  // Verify app metadata
  const { data: appData } = await app.octokit.request('GET /app')
  console.log('✅ Authentication Successful!')
  console.log(`   App Name:        ${appData.name}`)
  console.log(`   App URL:         ${appData.html_url}`)
  console.log(`   Owner:           ${appData.owner?.login || 'N/A'}`)
  console.log(`   Permissions:     ${JSON.stringify(appData.permissions, null, 2)}`)

  // Check installations
  console.log('\n--- Checking Installations ---')
  const { data: installations } = await app.octokit.request('GET /app/installations')
  
  if (installations.length === 0) {
    console.warn('⚠️ Warning: The app is not installed on any user or organization account.')
    console.log('   Please go to the App URL above, navigate to "Install App", and install it.')
  } else {
    console.log(`✅ Found ${installations.length} installations:`)
    
    for (const inst of installations) {
      console.log(`\n   • Installation ID: ${inst.id}`)
      console.log(`     Target Type:     ${inst.target_type}`)
      console.log(`     Account:         ${inst.account?.login}`)
      console.log(`     Repository Selection: ${inst.repository_selection}`)
      console.log(`     Permissions Grant:`)
      console.log(JSON.stringify(inst.permissions, null, 4))

      // Try to list accessible repositories
      try {
        const octokitInst = await app.getInstallationOctokit(inst.id)
        const { data: repoData } = await octokitInst.request('GET /installation/repositories')
        console.log(`     Accessible Repositories (${repoData.repositories.length}):`)
        repoData.repositories.forEach(repo => {
          console.log(`       - ${repo.full_name}`)
        })
      } catch (repoErr) {
        console.warn(`     ⚠️ Could not fetch repositories for this installation: ${repoErr.message}`)
      }
    }
  }
  
  // Verify OAuth Callback URL settings advice
  console.log('\n--- Gemini Enterprise Connection Guide ---')
  console.log('To link this GitHub App to Gemini Enterprise, confirm the following settings on GitHub:')
  console.log('1. Go to settings for the app on GitHub > General.')
  console.log('2. Ensure "Callback URL" is set exactly to: https://vertexaisearch.cloud.google.com/oauth-redirect')
  console.log('3. Ensure "Expire user authorization tokens" is Checked.')
  console.log('4. Ensure "Request user authorization (OAuth) during installation" is Checked.')
  console.log('5. Use the Client ID and Client Secret shown on the General tab when connecting in Google Cloud Console (NOT the App ID).')

} catch (err) {
  console.error('\n❌ Authentication Failed!')
  console.error(`   Error message: ${err.message}`)
  if (err.status === 401) {
    console.error('   Diagnostic: The private key or App ID is incorrect. Please verify they match in the GitHub UI.')
  }
}
