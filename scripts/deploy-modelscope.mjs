import { spawnSync } from 'node:child_process';
import { cpSync, existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';

const token = process.env.MODELSCOPE_API_KEY;
const studio = process.env.MODELSCOPE_STUDIO || 'ms-cookbook-team/ms-cookbook';
const endpoint = 'https://modelscope.cn';
if (!token) throw new Error('Set MODELSCOPE_API_KEY before deploying.');
if (!/^[\w-]+\/[\w-]+$/.test(studio)) throw new Error('Invalid MODELSCOPE_STUDIO.');

const source = resolve(import.meta.dirname, '..');
const temporary = mkdtempSync(join(tmpdir(), 'ms-cookbook-deploy-'));
const target = join(temporary, 'studio');
const askpass = join(temporary, 'git-askpass.sh');
writeFileSync(askpass, '#!/bin/sh\ncase "$1" in\n  *Username*) printf "%s" "oauth2" ;;\n  *Password*) printf "%s" "$MODELSCOPE_API_KEY" ;;\n  *) exit 1 ;;\nesac\n', { mode: 0o700 });
const gitEnvironment = {
  ...process.env,
  GIT_ASKPASS: askpass,
  GIT_TERMINAL_PROMPT: '0',
  GIT_CONFIG_COUNT: '1',
  GIT_CONFIG_KEY_0: 'credential.helper',
  GIT_CONFIG_VALUE_0: '',
};

function redact(value) {
  return String(value).split(token).join('[REDACTED]');
}

function run(command, args, cwd = source) {
  const result = spawnSync(command, args, {
    cwd, env: gitEnvironment, encoding: 'utf8', maxBuffer: 8 * 1024 * 1024,
    timeout: 5 * 60 * 1000,
  });
  if (result.status !== 0) {
    throw new Error(redact(`${command} failed: ${result.error?.message || result.stderr || result.stdout}`));
  }
  return result.stdout.trim();
}

async function api(path, method = 'GET') {
  const response = await fetch(`${endpoint}/openapi/v1${path}`, {
    method,
    headers: { Authorization: `Bearer ${token}` },
    signal: AbortSignal.timeout(90000),
  });
  const body = await response.json();
  if (!response.ok || !body.success) {
    throw new Error(redact(`ModelScope ${method} ${path}: HTTP ${response.status}, ${body.message || body.code}`));
  }
  return body.data;
}

try {
  const commit = run('git', ['rev-parse', 'HEAD']);
  const info = await api(`/studios/${studio}`);
  if (info.sdk_type && info.sdk_type !== 'docker') throw new Error('The target Studio must use Docker with OAuth enabled before deploying this version.');
  console.log(`Publishing GitHub commit ${commit} to ${studio}`);
  // Deploy on top of the current Studio commit; older history is not needed.
  // Retry interrupted downloads only, leaving authentication failures explicit.
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      // Fetch root files and tree metadata only. Large application directories
      // are replaced from GitHub below, so downloading their old blobs is wasteful.
      run('git', ['-c', 'http.version=HTTP/1.1', 'clone', '--filter=blob:none', '--sparse', '--depth', '1', '--no-tags', '--single-branch', '--branch', 'master', `${endpoint}/studios/${studio}.git`, target]);
      break;
    } catch (error) {
      if (attempt === 3 || !/early EOF|RPC failed|unexpected disconnect|timed out|ETIMEDOUT|Could not resolve host|Failed to connect/i.test(error.message)) throw error;
      console.log(`Studio download interrupted; retrying (${attempt}/2).`);
      // Only remove the incomplete clone created inside this run's temp directory.
      if (existsSync(target)) rmSync(target, { recursive: true });
      await new Promise(resolve => setTimeout(resolve, attempt * 2000));
    }
  }
  run('git', ['config', 'user.name', 'ms-cookbook deployment'], target);
  run('git', ['config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com'], target);

  // Export committed files only. Deployment scripts and credentials stay out of the site.
  const files = ['Dockerfile', 'requirements.txt', 'app.py', 'index.html', 'favicon.svg', 'assets', 'content', 'chapters', 'admin', 'CONTRIBUTING.md', 'README.md', 'README.zh-CN.md', 'LICENSE'];
  const archive = join(temporary, 'site.tar');
  const buildScripts=['scripts/build-content.py','scripts/chapter_markdown.py','scripts/version-assets.mjs'];
  run('git', ['archive', '--format=tar', '--output', archive, commit, '--', ...files, ...buildScripts]);
  // Sparse paths absent from disk otherwise keep their old index entries.
  // Reset only the three application-owned directories before importing them.
  run('git', ['rm', '-r', '-f', '--cached', '--sparse', '--ignore-unmatch', '--', 'assets', 'chapters', 'content'], target);
  // Replace the application-owned asset directory to remove obsolete images on updates.
  const oldAssets = join(target, 'assets');
  if (existsSync(oldAssets)) rmSync(oldAssets, { recursive: true });
  // The legacy chapter sources moved to content/; publish their migration guide.
  const oldChapters = join(target, 'chapters');
  if (existsSync(oldChapters)) rmSync(oldChapters, { recursive: true });
  // Mirror chapter moves and deletions from GitHub in this temporary clone.
  const oldContent = join(target, 'content');
  if (existsSync(oldContent)) rmSync(oldContent, { recursive: true });
  run('tar', ['-xf', archive, '-C', target]);
  // Always derive links and homepage counts from this release's committed data.
  run('python3',['scripts/build-content.py'],target);
  run('node',['scripts/version-assets.mjs'],target);
  rmSync(join(target,'scripts'),{recursive:true});

  cpSync(join(target, 'README.md'), join(target, 'README.en.md'));
  const chinese = readFileSync(join(target, 'README.zh-CN.md'), 'utf8')
    .replaceAll('href="README.md"', 'href="README.en.md"');
  const metadata = [
    '---', 'license: Apache License 2.0', 'language:', '- zh',
    'tags:', '- modelscope', '- cookbook', '- open-source-ai',
    '---', '',
  ].join('\n');
  writeFileSync(join(target, 'README.md'), metadata + chinese);
  writeFileSync(join(target, 'deployment.json'), JSON.stringify({
    repository: 'https://github.com/modelscope/ms-cookbook', commit,
  }, null, 2) + '\n');
  run('git', ['add', '--sparse', '--', ...files, 'README.en.md', 'deployment.json'], target);
  if (run('git', ['diff', '--cached', '--name-only'], target)) {
    run('git', ['commit', '-m', `Sync GitHub ms-cookbook ${commit.slice(0, 12)}`], target);
    run('git', ['push', 'origin', 'HEAD:master'], target);
    console.log('Studio repository synchronized.');
  } else {
    console.log('Studio repository already matches this commit.');
  }
  const result = await api(`/studios/${studio}/deploy`, 'POST');
  console.log(`Deployment requested: ${JSON.stringify(result)}`);
  let lastStatus;
  let verified = false;
  for (let attempt = 0; attempt < 60; attempt++) {
    const current = await api(`/studios/${studio}`);
    const status = current.runtime?.status || current.status;
    if (status !== lastStatus) console.log(`Studio status: ${status}`);
    lastStatus = status;
    if (/failed|error/i.test(status || '')) throw new Error(`Studio deployment failed: ${status}`);
    const host = current.host;
    if (String(status).toLowerCase() === 'running' && host) {
      const url = new URL(host);
      if (url.protocol !== 'https:' || !url.hostname.endsWith('.ms.show')) {
        throw new Error('Unexpected Studio application host.');
      }
      try {
        const response = await fetch(new URL('/deployment.json', url), {
          cache: 'no-store', signal: AbortSignal.timeout(15000),
        });
        if (response.ok && (await response.json()).commit === commit) {
          const page = await fetch(url, { signal: AbortSignal.timeout(15000) });
          if (page.ok && (await page.text()).includes('<title>魔搭紫皮书</title>')) {
            verified = true;
            console.log(`Verified deployed commit ${commit}: ${host}`);
            break;
          }
        }
      } catch {
        // The application host may become available shortly after the runtime starts.
      }
    }
    await new Promise(resolve => setTimeout(resolve, 10000));
  }
  if (!verified) throw new Error('Timed out waiting for the deployed commit to become publicly accessible.');
  console.log(`Studio: ${endpoint}/studios/${studio}`);
} catch (error) {
  console.error(redact(error.message));
  process.exitCode = 1;
} finally {
  rmSync(temporary, { recursive: true, force: true });
}
