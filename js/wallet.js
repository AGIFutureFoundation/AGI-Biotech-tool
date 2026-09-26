// MetaMask sign-in, and nothing else.
//
// This module connects a wallet, asks it to sign the server's EIP-4361 message,
// and exchanges the signature for a session token. That is the whole surface.
// It deliberately cannot send a transaction, and exposes no method that could:
// the only RPC calls it makes are eth_requestAccounts, eth_chainId and
// personal_sign. A wallet prompt from this file can never move funds, and a
// user who has learned that can click through ours without reading -- which
// they will -- without that habit costing them anything elsewhere.
//
// Anchoring a Merkle root DOES require a transaction, and that lives in
// chain_anchor.py on the server, which builds an unsigned payload for a person
// to review and sign in their own wallet. Signing is not automated from here.

// Monad testnet. Kept in sync with chain_anchor.NETWORKS and SIWE_CHAIN_ID.
export const MONAD_TESTNET = {
  chainId: '0x279f',                       // 10143
  chainName: 'Monad Testnet',
  nativeCurrency: { name: 'MON', symbol: 'MON', decimals: 18 },
  rpcUrls: ['https://rpc.testnet.monad.xyz'],
  blockExplorerUrls: ['https://testnet.monadscan.com'],
};

export const NO_WALLET =
  'No Ethereum wallet detected. Install MetaMask, or sign in with email instead. ' +
  'Wallet sign-in is optional: it proves authorship of a record, it is not required to browse.';

function provider() {
  // EIP-1193. Several wallets inject here; we do not care which, only that it
  // speaks the standard.
  return typeof window !== 'undefined' ? window.ethereum : undefined;
}

export function hasWallet() {
  return Boolean(provider());
}

/** Connect, returning the selected address. Throws with a readable message. */
export async function connect() {
  const eth = provider();
  if (!eth) throw new Error(NO_WALLET);

  let accounts;
  try {
    accounts = await eth.request({ method: 'eth_requestAccounts' });
  } catch (err) {
    // 4001 is the user closing the prompt. That is a choice, not a fault, and
    // should not surface as a stack trace or a red error banner.
    if (err && err.code === 4001) throw new Error('Sign-in cancelled.');
    throw new Error(`Wallet connection failed: ${err?.message || err}`);
  }
  if (!accounts || !accounts.length) throw new Error('Wallet returned no account.');
  return accounts[0];
}

/** The chain the wallet is currently on, as a decimal number. */
export async function currentChainId() {
  const eth = provider();
  if (!eth) throw new Error(NO_WALLET);
  return parseInt(await eth.request({ method: 'eth_chainId' }), 16);
}

/**
 * Ask the wallet to switch to Monad testnet, adding it if unknown.
 *
 * Returns true if we are on the right chain afterwards. A refusal is not an
 * error: signing in on the wrong chain simply fails the server's check, and
 * telling the user that is better than a silent retry loop.
 */
export async function ensureMonad(network = MONAD_TESTNET) {
  const eth = provider();
  if (!eth) throw new Error(NO_WALLET);

  try {
    await eth.request({ method: 'wallet_switchEthereumChain',
                        params: [{ chainId: network.chainId }] });
    return true;
  } catch (err) {
    if (err && err.code === 4902) {        // chain not known to the wallet
      await eth.request({ method: 'wallet_addEthereumChain', params: [network] });
      return true;
    }
    if (err && err.code === 4001) return false;
    throw err;
  }
}

/**
 * Full sign-in: fetch the server's nonce and message, sign it, exchange it.
 *
 * The message comes FROM the server, with a nonce the server minted. We only
 * substitute the address line. Letting the client compose its own message would
 * let it choose its own nonce, and a self-chosen nonce is no nonce at all.
 */
export async function signIn({ base = '', address } = {}) {
  const eth = provider();
  if (!eth) throw new Error(NO_WALLET);

  const account = address || await connect();

  const res = await fetch(`${base}/api/auth/nonce`);
  if (!res.ok) throw new Error(`Could not get a sign-in nonce (${res.status}).`);
  const challenge = await res.json();

  // The server renders the message with a placeholder address because it does
  // not know which account is connected until now.
  const message = challenge.message.replace(
    /^0x0{40}$/m, account);

  let signature;
  try {
    signature = await eth.request({ method: 'personal_sign', params: [message, account] });
  } catch (err) {
    if (err && err.code === 4001) throw new Error('Signature declined.');
    throw new Error(`Signing failed: ${err?.message || err}`);
  }

  const out = await fetch(`${base}/api/auth/siwe`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, signature }),
  });
  const body = await out.json().catch(() => ({}));
  if (!out.ok || !body.ok) {
    throw new Error(body.error || `Sign-in rejected (${out.status}).`);
  }
  return { token: body.token, address: body.address,
           interopVerified: Boolean(body.interop_verified) };
}

/** Short display form. Full addresses are unreadable and invite mis-verification. */
export function shortAddress(address) {
  if (!address || address.length < 10) return address || '';
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
}

/**
 * Fire `onChange` when the wallet switches account or chain.
 *
 * A session token is bound to the address that signed for it, so an account
 * switch has to end the session rather than silently leave the user acting as
 * someone else. Returns an unsubscribe function.
 */
export function watchWallet(onChange) {
  const eth = provider();
  if (!eth || !eth.on) return () => {};

  const accountsChanged = (accounts) =>
    onChange({ reason: 'accountsChanged', address: accounts?.[0] || null });
  const chainChanged = (chainId) =>
    onChange({ reason: 'chainChanged', chainId: parseInt(chainId, 16) });

  eth.on('accountsChanged', accountsChanged);
  eth.on('chainChanged', chainChanged);

  return () => {
    eth.removeListener?.('accountsChanged', accountsChanged);
    eth.removeListener?.('chainChanged', chainChanged);
  };
}
