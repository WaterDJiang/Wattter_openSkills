import { CliError } from '@jackwener/opencli/errors';
import { cli, Strategy } from '@jackwener/opencli/registry';
import {
  assertHttp,
  assertNoLocalImages,
  draftResult,
  formBody,
  getCookieHeader,
  parseJson,
  readPayloadFile,
  request,
  requireExecute,
} from '../_wtt_post/shared.js';

function requestId(uid) {
  const source = Buffer.from(`${uid}&${Date.now()}`).toString('base64url');
  const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';
  let value = source;
  while (value.length < 43) value += alphabet[Math.floor(Math.random() * alphabet.length)];
  return value.slice(0, 43);
}

async function postForm(url, cookie, values, reqId) {
  const result = await request(url, {
    method: 'POST',
    headers: {
      Cookie: cookie,
      Origin: 'https://card.weibo.com',
      Referer: 'https://card.weibo.com/article/v5/editor',
      Accept: 'application/json, text/plain, */*',
      'Content-Type': 'application/x-www-form-urlencoded',
      'SN-REQID': reqId,
    },
    body: formBody(values),
  });
  assertHttp(result.response, result.text, '微博长文草稿请求');
  return parseJson(result.text, '微博长文草稿请求');
}

cli({
  site: 'weibo',
  name: 'article-draft',
  access: 'write',
  description: '使用浏览器登录态创建微博长文草稿（无 CSDN 插件）',
  domain: 'card.weibo.com',
  strategy: Strategy.COOKIE,
  browser: true,
  navigateBefore: false,
  args: [
    { name: 'title', required: true, help: '长文标题' },
    { name: 'file', required: true, help: '已适配的 UTF-8 HTML 文件' },
    { name: 'summary', help: '长文摘要' },
    { name: 'cover-url', help: '已由微博托管的封面 URL' },
    { name: 'execute', type: 'boolean', help: '确认创建草稿' },
  ],
  columns: ['status', 'write_state', 'provider', 'platform', 'account', 'draft_id', 'draft_url', 'detail'],
  func: async (page, kwargs) => {
    requireExecute(kwargs);
    const title = String(kwargs.title || '').trim();
    if (!title) throw new CliError('INVALID_INPUT', '--title is required');
    const html = await readPayloadFile(kwargs.file);
    assertNoLocalImages(html);
    const cookie = await getCookieHeader(page, ['https://card.weibo.com/', 'https://weibo.com/']);

    const editorResponse = await request('https://card.weibo.com/article/v5/editor', { headers: { Cookie: cookie } });
    assertHttp(editorResponse.response, editorResponse.text, '检查微博长文登录态');
    const encodedConfig = editorResponse.text.match(/config:\s*JSON\.parse\('(.+?)'\)/)?.[1];
    if (!encodedConfig) throw new CliError('AUTH_REQUIRED', '未识别到微博长文登录账号');
    let identity;
    try {
      identity = JSON.parse(encodedConfig.replace(/\\'/g, "'").replace(/\\\\/g, '\\'));
    } catch {
      throw new CliError('API_ERROR', '微博长文账号配置解析失败');
    }
    if (!identity.uid) throw new CliError('AUTH_REQUIRED', '微博长文账号缺少 uid');
    const uid = String(identity.uid);

    const createReqId = requestId(uid);
    const created = await postForm(
      `https://card.weibo.com/article/v5/aj/editor/draft/create?uid=${uid}&_rid=${createReqId}`,
      cookie,
      {},
      createReqId,
    );
    if (Number(created.code) !== 100000 || !created?.data?.id) {
      throw new CliError('API_ERROR', created.msg || '微博长文草稿响应缺少 ID');
    }
    const draftId = String(created.data.id);
    const saveReqId = requestId(uid);
    const saved = await postForm(
      `https://card.weibo.com/article/v5/aj/editor/draft/save?uid=${uid}&id=${draftId}&_rid=${saveReqId}`,
      cookie,
      {
        id: draftId, title, subtitle: '', type: '', status: '0', publish_at: '',
        error_msg: '', error_code: '0', collection: '[]', free_content: '', content: html,
        cover: String(kwargs['cover-url'] || ''), summary: String(kwargs.summary || ''),
        writer: '', extra: 'null', is_word: '0', article_recommend: '[]',
        follow_to_read: '1', isreward: '1', pay_setting: '{"ispay":0,"isvclub":0}',
        source: '0', action: '1', content_type: '0', save: '1',
      },
      saveReqId,
    );
    if (String(saved.code) !== '100000') {
      throw new CliError('WRITE_UNKNOWN', `微博长文草稿 ${draftId} 已创建，但保存响应异常；先对账，不得自动重试`);
    }
    return draftResult({
      platform: 'weibo',
      account: identity.nick || uid,
      draftId,
      draftUrl: `https://card.weibo.com/article/v5/editor#/draft/${draftId}`,
    });
  },
});

