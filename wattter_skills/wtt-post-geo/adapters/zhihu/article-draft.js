import { CliError } from '@jackwener/opencli/errors';
import { cli, Strategy } from '@jackwener/opencli/registry';
import {
  assertHttp,
  assertNoLocalImages,
  draftResult,
  getCookieHeader,
  parseJson,
  readPayloadFile,
  request,
  requireExecute,
} from '../_wtt_post/shared.js';

cli({
  site: 'zhihu',
  name: 'article-draft',
  access: 'write',
  description: '使用浏览器登录态创建知乎专栏草稿（无 CSDN 插件）',
  domain: 'zhuanlan.zhihu.com',
  strategy: Strategy.COOKIE,
  browser: true,
  navigateBefore: false,
  args: [
    { name: 'title', required: true, help: '文章标题' },
    { name: 'file', required: true, help: '已适配的 UTF-8 HTML 文件' },
    { name: 'execute', type: 'boolean', help: '确认创建草稿' },
  ],
  columns: ['status', 'write_state', 'provider', 'platform', 'account', 'draft_id', 'draft_url', 'detail'],
  func: async (page, kwargs) => {
    requireExecute(kwargs);
    const title = String(kwargs.title || '').trim();
    if (!title) throw new CliError('INVALID_INPUT', '--title is required');
    const content = await readPayloadFile(kwargs.file);
    assertNoLocalImages(content);
    const cookie = await getCookieHeader(page, ['https://www.zhihu.com/', 'https://zhuanlan.zhihu.com/']);
    const commonHeaders = { Cookie: cookie, 'x-requested-with': 'fetch' };

    const meResponse = await request('https://www.zhihu.com/api/v4/me', { headers: commonHeaders });
    assertHttp(meResponse.response, meResponse.text, '检查知乎登录态');
    const me = parseJson(meResponse.text, '检查知乎登录态');
    if (!me.id) throw new CliError('AUTH_REQUIRED', '未识别到知乎登录账号');

    const createdResponse = await request('https://zhuanlan.zhihu.com/api/articles/drafts', {
      method: 'POST',
      headers: { ...commonHeaders, 'Content-Type': 'application/json', Origin: 'https://zhuanlan.zhihu.com', Referer: 'https://zhuanlan.zhihu.com/write' },
      body: JSON.stringify({ title, content: '', delta_time: 0 }),
    });
    assertHttp(createdResponse.response, createdResponse.text, '创建知乎草稿');
    const created = parseJson(createdResponse.text, '创建知乎草稿');
    if (!created.id) throw new CliError('API_ERROR', '知乎草稿响应缺少 ID');

    const updatedResponse = await request(`https://zhuanlan.zhihu.com/api/articles/${created.id}/draft`, {
      method: 'PATCH',
      headers: { ...commonHeaders, 'Content-Type': 'application/json', Origin: 'https://zhuanlan.zhihu.com', Referer: 'https://zhuanlan.zhihu.com/write' },
      body: JSON.stringify({ title, content }),
    });
    if (!updatedResponse.response.ok) {
      throw new CliError('WRITE_UNKNOWN', `知乎草稿 ${created.id} 已创建，但正文更新失败；先对账，不得自动重试`);
    }
    return draftResult({
      platform: 'zhihu',
      account: me.name || me.url_token || me.id,
      draftId: created.id,
      draftUrl: `https://zhuanlan.zhihu.com/p/${created.id}/edit`,
    });
  },
});

