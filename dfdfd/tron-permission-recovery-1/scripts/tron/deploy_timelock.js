const TronWeb = require('tronweb');
const fs = require('fs');
const path = require('path');

async function main() {
  const rpcUrl = process.env.TRON_RPC_URL || 'https://api.trongrid.io';
  const privateKey = process.env.TRON_PRIVATE_KEY;
  const fullHost = process.env.TRON_FULL_HOST || rpcUrl;

  if (!privateKey) {
    console.error('Missing TRON_PRIVATE_KEY environment variable.');
    process.exit(1);
  }

  const artifactPath = path.join(__dirname, 'TimelockController.json');
  if (!fs.existsSync(artifactPath)) {
    console.error(`Missing ABI artifact: ${artifactPath}`);
    console.error('Please compile a TimelockController contract artifact first and place it at scripts/tron/TimelockController.json');
    process.exit(1);
  }

  const artifact = JSON.parse(fs.readFileSync(artifactPath, 'utf8'));
  const tronWeb = new TronWeb({
    fullHost,
    privateKey,
    headers: { 'TRON-PRO-API-KEY': process.env.TRON_API_KEY || '' },
  });

  const minDelay = Number(process.env.MIN_DELAY || 3600);
  const proposers = (process.env.PROPOSERS || '').split(',').filter(Boolean);
  const executors = (process.env.EXECUTORS || '').split(',').filter(Boolean);

  if (proposers.length === 0 || executors.length === 0) {
    console.error('PROPOSERS and EXECUTORS must be set to at least one address each.');
    process.exit(1);
  }

  const contract = await tronWeb.contract().new({
    abi: artifact.abi,
    bytecode: artifact.bytecode,
    parameters: [minDelay, proposers, executors],
  });

  console.log('TimelockController deployment successful.');
  console.log('Contract address:', contract.address);
}

main().catch((err) => {
  console.error('Deployment failed:', err);
  process.exit(1);
});
