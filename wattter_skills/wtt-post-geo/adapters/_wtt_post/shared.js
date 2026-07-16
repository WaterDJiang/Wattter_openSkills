import { readFile, stat } from 'node:fs/promises';
import { CliError } from '@jackwener/opencli/errors';

const USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/140 Safari/537.36';

export function requireExecute(kwargs) {
  if (!kwargs.execute) {
    throw new CliError('INVALID_INPUT', 'Creating a platform draft requires --execute');
  }
}

export async function readPayloadFile(filePath) {
  const path = String(filePath || '').trim();
  if (!path) throw new CliError('INVALID_INPUT', '--file is required');
  let info;
  try {
    info = await stat(path);
  } catch {
    throw new CliError('INVALID_INPUT', `File not found: ${path}`);
  }
  if (!info.isFile()) throw new CliError('INVALID_INPUT', `Not a readable file: ${path}`);
  let content;
  try {
    content = await readFile(path, 'utf8');
  } catch {
    throw new CliError('INVALID_INPUT', `Could not read UTF-8 file: ${path}`);
  }
  if (!content.trim()) throw new CliError('INVALID_INPUT', `Payload file is empty: ${path}`);
  return content;
}

export function assertNoLocalImages(content) {
  const localPatterns = [
    /(?:src|href)=["'](?:file:\/\/|\/Users\/|\/private\/|\.\.?\/)/i,
    /!\[[^\]]*\]\((?:file:\/\/|\/Users\/|\/private\/|\.\.?\/)/i,
  ];
  if (localPatterns.some((pattern) => pattern.test(content))) {
    throw new CliError(
      'INVALID_INPUT',
      'Payload contains local image paths. Use a platform-hosted URL or route this platform through the image-capable UI fallback.',
    );
  }
}

export async function getCookieHeader(page, urls) {
  if (!page) throw new CliError('BROWSER_REQUIRED', 'OpenCLI browser bridge is required');
  const cookies = new Map();
  for (const url of urls) {
    try {
      for (const cookie of await page.getCookies({ url })) {
        if (!cookies.has(cookie.name)) cookies.set(cookie.name, cookie.value);
      }
    } catch {
      // Try the next related origin. Authentication is validated by the API response.
    }
  }
  if (!cookies.size) throw new CliError('AUTH_REQUIRED', `No login cookies found for ${urls[0]}`);
  return [...cookies].map(([name, value]) => `${name}=${value}`).join('; ');
}

export async function request(url, options = {}) {
  const headers = {
    'User-Agent': USER_AGENT,
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    ...(options.headers || {}),
  };
  const response = await fetch(url, { ...options, headers, redirect: 'follow' });
  const text = await response.text();
  if (response.status === 401 || response.status === 403) {
    throw new CliError('AUTH_REQUIRED', `Login expired or permission denied: HTTP ${response.status}`);
  }
  return { response, text };
}

export function parseJson(text, label) {
  try {
    return JSON.parse(text);
  } catch {
    throw new CliError('API_ERROR', `${label} returned invalid JSON: ${shortText(text)}`);
  }
}

export function assertHttp(response, text, label) {
  if (!response.ok) {
    throw new CliError('HTTP_ERROR', `${label} failed: HTTP ${response.status} ${shortText(text)}`);
  }
}

export function shortText(value, limit = 180) {
  const text = String(value || '').replace(/\s+/g, ' ').trim();
  return text.length > limit ? `${text.slice(0, limit)}...` : text;
}

export function draftResult({ platform, account, draftId, draftUrl, detail = 'Draft created; target-platform readback still required' }) {
  return [{
    status: 'success',
    write_state: 'created_unverified',
    provider: 'opencli_login_adapter',
    platform,
    account: String(account || ''),
    draft_id: String(draftId),
    draft_url: draftUrl,
    detail,
  }];
}

export function accountResult({ platform, account, accountId }) {
  return [{
    status: 'authenticated',
    platform,
    account: String(account || ''),
    account_id: String(accountId || ''),
  }];
}

export function parseCsv(value) {
  return String(value || '').split(',').map((item) => item.trim()).filter(Boolean);
}

export function formBody(values) {
  return new URLSearchParams(Object.entries(values).map(([key, value]) => [key, String(value ?? '')]));
}
